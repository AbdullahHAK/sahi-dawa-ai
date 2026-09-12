"""Sahi Dawa backend entry point.

Currently exposes the deterministic catalogue/matching/pricing layer.
RAG explanation, patient history and pattern detection are separate
layers to be wired in on top of this by other services.
"""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Sahi Dawa API")

app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
