import json
import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from app.db import close_db, get_pool, init_db
from app.events import Event, now_utc, project_state
from app.observability import setup_observability


def _parse_cors_origins(value: str) -> List[str]:
    # Accept comma-separated list or a single origin.
    origins = [v.strip() for v in value.split(",") if v.strip()]
    return origins or ["http://localhost:3000"]


app = FastAPI(title="trainer2-api")

setup_observability(app, os.getenv("OTEL_SERVICE_NAME", "trainer2-api"))

logger = logging.getLogger("trainer2.api")


def _stub_coach_reply(message: str) -> str:
    text = message.strip().lower()
    if not text:
        return "Tell me what you want to train today."

    if any(w in text for w in ["hello", "hi", "hey", "yo"]):
        return "Hey. What are we training today — and what equipment do you have?"

    if "leg" in text:
        return (
            "Leg day. Quick setup questions: do you have a barbell, rack, and plates? "
            "Any knee/back issues?"
        )
    if "push" in text or "bench" in text or "chest" in text:
        return (
            "Push day. Do you have a bench + barbell/dumbbells? "
            "Any shoulder pain or limitations?"
        )
    if "pull" in text or "back" in text:
        return (
            "Pull day. What do you have available (pull-up bar, row machine, dumbbells)? "
            "Any elbow/bicep issues?"
        )

    return (
        "Got it. Give me: (1) goal (strength/hypertrophy/fat loss), "
        "(2) experience level, (3) time available today, and (4) equipment."
    )


class EventIn(BaseModel):
    type: str = Field(min_length=1)
    payload: Dict[str, Any]
    sessionId: Optional[str] = None


class EventAck(BaseModel):
    id: str
    ts: str
    type: str


@app.on_event("startup")
async def _startup() -> None:
    await init_db(app)


@app.on_event("shutdown")
async def _shutdown() -> None:
    await close_db(app)

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
chat_backend = os.getenv("CHAT_BACKEND", "stub").strip().lower()

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


@app.post("/events", response_model=EventAck)
async def append_event(event: EventIn) -> EventAck:
    event_id = str(uuid.uuid4())
    ts = now_utc()
    payload_json = json.dumps(event.payload)

    pool = get_pool(app)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO events (id, ts, type, session_id, payload)
            VALUES ($1, $2, $3, $4, $5::jsonb)
            """,
            event_id,
            ts,
            event.type,
            event.sessionId,
            payload_json,
        )

    return EventAck(id=event_id, ts=ts.isoformat(), type=event.type)


@app.get("/state")
async def get_state() -> Dict[str, Any]:
    pool = get_pool(app)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id::text as id,
                   ts,
                   type,
                   session_id,
                   payload
            FROM events
            ORDER BY ts ASC, id ASC
            """
        )

    events: List[Event] = []
    for r in rows:
        raw_payload = r["payload"]
        if isinstance(raw_payload, str):
            payload = json.loads(raw_payload)
        else:
            payload = raw_payload
        events.append(
            Event(
                id=r["id"],
                ts=r["ts"],
                type=r["type"],
                sessionId=r["session_id"],
                payload=dict(payload),
            )
        )

    snapshot = project_state(events)
    last = events[-1] if events else None
    return {
        "meta": {
            "eventsCount": len(events),
            "lastEventId": last.id if last else None,
            "lastEventTs": last.ts.isoformat() if last else None,
        },
        "snapshot": snapshot,
    }


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
    client: Optional[httpx.AsyncClient] = None
    if chat_backend == "http":
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
                if chat_backend == "http":
                    if client is None:
                        raise RuntimeError("CHAT_BACKEND=http but no client")
                    started = time.perf_counter()
                    response = await client.post(
                        f"{agent_base_url}/respond",
                        json={"sessionId": session_id, "message": message},
                    )
                    response.raise_for_status()
                    agent_result: Any = response.json()
                    agent_calls_total.labels(status="success").inc()
                    agent_call_duration_seconds.observe(time.perf_counter() - started)

                    if not isinstance(agent_result, dict):
                        raise ValueError("agent returned invalid response")

                    text = str(agent_result.get("text", ""))
                    a2ui_actions = agent_result.get("a2uiActions", [])
                else:
                    text = _stub_coach_reply(message)
                    a2ui_actions = []
            except Exception as exc:
                agent_calls_total.labels(status="error").inc()
                await ws.send_json(
                    {
                        "type": "error",
                        "sessionId": session_id,
                        "requestId": request_id,
                        "message": f"chat backend failed: {exc}",
                    }
                )
                logger.exception(
                    "chat backend failed",
                    extra={"sessionId": session_id, "requestId": request_id},
                )
                continue

            await ws.send_json(
                {
                    "type": "chat.message",
                    "sessionId": session_id,
                    "role": "assistant",
                    "message": text,
                    "requestId": request_id,
                }
            )

            if isinstance(a2ui_actions, list) and a2ui_actions:
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
        if client is not None:
            await client.aclose()
