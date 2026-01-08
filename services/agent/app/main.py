import json
import logging
import os
import time

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response
from starlette.responses import StreamingResponse

from app.capabilities_sync import update_capabilities
from app.observability import setup_observability
from app.runner import run_stream
from app.schemas import RunRequest

import agents.tracing as agents_tracing

app = FastAPI(title="trainer2-agent")

setup_observability(app, os.getenv("OTEL_SERVICE_NAME", "trainer2-agent"))

logger = logging.getLogger("trainer2.agent")


@app.on_event("startup")
async def _startup() -> None:
    # Best-effort: materialize API tool surface into auditable files.
    if os.getenv("AGENT_PRIVATE_KEY", "").strip() or os.getenv("AGENT_PRIVATE_KEY_B64", "").strip():
        try:
            await update_capabilities()
        except Exception:
            logger.exception("capabilities_update_failed")

    # OpenAI Agents SDK tracing -> OpenAI dashboard.
    if os.getenv("OPENAI_AGENTS_DISABLE_TRACING", "0").strip() not in ("1", "true", "True"):
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if api_key:
            try:
                agents_tracing.set_tracing_export_api_key(api_key)
            except Exception:
                logger.exception("agents_tracing_setup_failed")

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



@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/update")
async def update() -> dict:
    # Developer ergonomics: fetch API surface and materialize to files.
    return await update_capabilities()


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


@app.post("/run")
async def run(payload: RunRequest) -> StreamingResponse:
    async def gen():
        async for evt in run_stream(
            user_id=payload.userId,
            session_id=payload.sessionId,
            message=payload.message,
            context=payload.context,
            max_turns=payload.maxTurns,
        ):
            yield (json.dumps(evt, ensure_ascii=False) + "\n").encode("utf-8")

    return StreamingResponse(gen(), media_type="application/x-ndjson")
