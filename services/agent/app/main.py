from fastapi import FastAPI

app = FastAPI(title="trainer2-agent")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
