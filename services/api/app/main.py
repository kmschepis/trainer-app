import logging
import os
import time
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.db import close_db, init_db
from app.metrics import http_request_duration_seconds, http_requests_total
from app.observability import setup_observability
from app.routes.events import router as events_router
from app.routes.realtime import router as realtime_router


def _parse_cors_origins(value: str) -> List[str]:
    # Accept comma-separated list or a single origin.
    origins = [v.strip() for v in value.split(",") if v.strip()]
    return origins or ["http://localhost:3000"]


app = FastAPI(title="trainer2-api")

setup_observability(app, os.getenv("OTEL_SERVICE_NAME", "trainer2-api"))

logger = logging.getLogger("trainer2.api")


app.include_router(events_router)
app.include_router(realtime_router)


@app.on_event("startup")
async def _startup() -> None:
    await init_db(app)


@app.on_event("shutdown")
async def _shutdown() -> None:
    await close_db(app)

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
