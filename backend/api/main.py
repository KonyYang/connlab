"""Minimal FastAPI application for the ConnLab scaffold."""

from fastapi import FastAPI


app = FastAPI(title="ConnLab API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
