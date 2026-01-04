import logging
import os
import time
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from app.observability import setup_observability

app = FastAPI(title="trainer2-agent")

setup_observability(app, os.getenv("OTEL_SERVICE_NAME", "trainer2-agent"))

logger = logging.getLogger("trainer2.agent")


def _load_system_prompt() -> str:
    prompt_path = os.getenv("AGENT_SYSTEM_PROMPT_PATH", "").strip()
    if prompt_path:
        path = Path(prompt_path)
    else:
        path = Path(__file__).parent / "prompts" / "system.txt"

    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return (
            "You are an elite strength coach. Keep replies concise and practical. "
            "Ask clarifying questions when needed."
        )

def _openai_compatible_reply(*, session_id: str, message: str, context: Optional[Dict[str, Any]]) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")

    if not api_key or not model:
        raise ValueError("missing OPENAI_API_KEY or OPENAI_MODEL")

    system = _load_system_prompt()

    messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
    if context:
        messages.append(
            {
                "role": "system",
                "content": "Context (JSON):\n" + json.dumps(context, ensure_ascii=False),
            }
        )
    messages.append({"role": "user", "content": message})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.6,
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()

    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("LLM returned no choices")

    msg = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = msg.get("content") if isinstance(msg, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM returned empty content")

    # Do not log the prompt or API key.
    logger.info("llm_response", extra={"sessionId": session_id, "model": model})
    return content.strip()

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
    context: Optional[Dict[str, Any]] = None


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
    # Always LLM-backed. If the LLM is not configured, return an error.
    started = time.perf_counter()
    respond_calls_total.inc()

    try:
        text = _openai_compatible_reply(
            session_id=payload.sessionId,
            message=payload.message,
            context=payload.context,
        )
    except Exception as exc:
        logger.exception("agent_respond_failed", extra={"sessionId": payload.sessionId})
        raise HTTPException(
            status_code=500,
            detail=(
                "Agent failed to generate a response. "
                "Check OPENAI_API_KEY / OPENAI_MODEL (and optionally OPENAI_BASE_URL). "
                f"Error: {exc}"
            ),
        )

    respond_duration_seconds.observe(time.perf_counter() - started)
    logger.info("responded", extra={"sessionId": payload.sessionId})
    return RespondResponse(text=text, a2uiActions=[])
