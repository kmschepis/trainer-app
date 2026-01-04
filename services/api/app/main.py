import os
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware


def _parse_cors_origins(value: str) -> List[str]:
    # Accept comma-separated list or a single origin.
    origins = [v.strip() for v in value.split(",") if v.strip()]
    return origins or ["http://localhost:3000"]


app = FastAPI(title="trainer2-api")

cors_origins = _parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:3000"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.websocket("/realtime")
async def realtime(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            message = await ws.receive_text()
            await ws.send_text(message)
    except WebSocketDisconnect:
        return
