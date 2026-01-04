import logging
import os
import time
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from app.observability import setup_observability

app = FastAPI(title="trainer2-agent")

setup_observability(app, os.getenv("OTEL_SERVICE_NAME", "trainer2-agent"))

logger = logging.getLogger("trainer2.agent")

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

respond_calls_total = Counter(
    "respond_calls_total",
    "Total /respond calls",
)
respond_duration_seconds = Histogram(
    "respond_duration_seconds",
    "Respond duration (seconds)",
)


class RespondRequest(BaseModel):
    sessionId: str
    message: str


class RespondResponse(BaseModel):
    text: str
    a2uiActions: List[Dict[str, Any]] = Field(default_factory=list)


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


@app.post("/respond", response_model=RespondResponse)
def respond(payload: RespondRequest) -> RespondResponse:
    # Phase 0/003: stub behavior. Phase 1 will plug in real agent logic.
    started = time.perf_counter()
    respond_calls_total.inc()
    text = f"ACK ({payload.sessionId}): {payload.message}"

    actions: List[Dict[str, Any]] = [
        {
            "type": "ui.toast",
            "message": "received chat.send",
        }
    ]

    respond_duration_seconds.observe(time.perf_counter() - started)
    logger.info("responded", extra={"sessionId": payload.sessionId})
    return RespondResponse(text=text, a2uiActions=actions)
