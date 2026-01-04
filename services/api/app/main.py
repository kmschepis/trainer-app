import json
import logging
import os
import time
import uuid
from typing import Any, List, Optional

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from app.observability import setup_observability


def _parse_cors_origins(value: str) -> List[str]:
    # Accept comma-separated list or a single origin.
    origins = [v.strip() for v in value.split(",") if v.strip()]
    return origins or ["http://localhost:3000"]


app = FastAPI(title="trainer2-api")

setup_observability(app, os.getenv("OTEL_SERVICE_NAME", "trainer2-api"))

logger = logging.getLogger("trainer2.api")

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["method", "path", "status"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration (seconds)",
    labelnames=["method", "path"],
)

ws_messages_total = Counter(
    "ws_messages_total",
    "Total websocket messages received",
    labelnames=["type"],
)
agent_calls_total = Counter(
    "agent_calls_total",
    "Total agent calls",
    labelnames=["status"],
)
agent_call_duration_seconds = Histogram(
    "agent_call_duration_seconds",
    "Agent call duration (seconds)",
)

agent_base_url = os.getenv("AGENT_BASE_URL", "http://agent:9000")

cors_origins = _parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:3000"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.middleware("http")
async def prometheus_http_metrics(request, call_next):
    path = request.url.path
    method = request.method
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    http_requests_total.labels(method=method, path=path, status=str(response.status_code)).inc()
    http_request_duration_seconds.labels(method=method, path=path).observe(duration)
    return response


@app.websocket("/realtime")
async def realtime(ws: WebSocket) -> None:
    await ws.accept()

    session_id: Optional[str] = None
    client = httpx.AsyncClient(timeout=10.0)
    try:
        while True:
            raw = await ws.receive_text()

            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                # Back-compat with Phase 0: echo raw text.
                await ws.send_text(raw)
                continue

            if not isinstance(payload, dict):
                await ws.send_json({"type": "error", "message": "invalid payload"})
                continue

            msg_type = payload.get("type")
            request_id = payload.get("requestId")

            if isinstance(msg_type, str):
                ws_messages_total.labels(type=msg_type).inc()

            if msg_type == "ping":
                await ws.send_json({"type": "pong", "requestId": request_id})
                continue

            if msg_type != "chat.send":
                await ws.send_json(
                    {
                        "type": "error",
                        "requestId": request_id,
                        "message": f"unsupported type: {msg_type}",
                    }
                )
                continue

            incoming_session_id = payload.get("sessionId")
            if incoming_session_id and isinstance(incoming_session_id, str):
                session_id = incoming_session_id
            if not session_id:
                session_id = str(uuid.uuid4())
                await ws.send_json(
                    {"type": "session.created", "sessionId": session_id, "requestId": request_id}
                )

            message = payload.get("message")
            if not isinstance(message, str) or not message.strip():
                await ws.send_json(
                    {
                        "type": "error",
                        "sessionId": session_id,
                        "requestId": request_id,
                        "message": "message must be a non-empty string",
                    }
                )
                continue

            try:
                started = time.perf_counter()
                response = await client.post(
                    f"{agent_base_url}/respond",
                    json={"sessionId": session_id, "message": message},
                )
                response.raise_for_status()
                agent_result: Any = response.json()
                agent_calls_total.labels(status="success").inc()
                agent_call_duration_seconds.observe(time.perf_counter() - started)
            except Exception as exc:
                agent_calls_total.labels(status="error").inc()
                await ws.send_json(
                    {
                        "type": "error",
                        "sessionId": session_id,
                        "requestId": request_id,
                        "message": f"agent call failed: {exc}",
                    }
                )
                logger.exception(
                    "agent call failed",
                    extra={"sessionId": session_id, "requestId": request_id},
                )
                continue

            if not isinstance(agent_result, dict):
                await ws.send_json(
                    {
                        "type": "error",
                        "sessionId": session_id,
                        "requestId": request_id,
                        "message": "agent returned invalid response",
                    }
                )
                continue

            text = agent_result.get("text", "")
            await ws.send_json(
                {
                    "type": "chat.message",
                    "sessionId": session_id,
                    "role": "assistant",
                    "message": text,
                    "requestId": request_id,
                }
            )

            a2ui_actions = agent_result.get("a2uiActions", [])
            if isinstance(a2ui_actions, list):
                for action in a2ui_actions:
                    await ws.send_json(
                        {
                            "type": "a2ui.action",
                            "sessionId": session_id,
                            "action": action,
                            "requestId": request_id,
                        }
                    )
    except WebSocketDisconnect:
        return
    finally:
        await client.aclose()
