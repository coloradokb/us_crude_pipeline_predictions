from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from pipeline_pred.config import load_settings
from pipeline_pred.storage import database


app = FastAPI(title="WCESTUS1 Pipeline Predictions", version="0.1.0")
settings = load_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _row_to_dict(row: Any) -> dict[str, Any]:
    return dict(row)


@app.get("/health")
def health() -> dict[str, str]:
    settings = load_settings()
    return {
        "status": "ok",
        "database": "available" if database.database_exists(settings.database_url) else "missing",
    }


@app.get("/observations")
def observations(series: str = Query(default="WCESTUS1")) -> list[dict[str, Any]]:
    settings = load_settings()
    with database.connection(settings.database_url) as conn:
        database.initialize(conn)
        rows = database.get_series(conn, "observations", series)
    return [_row_to_dict(row) for row in rows]


@app.get("/predictions")
def predictions(series: str = Query(default="WCESTUS1")) -> list[dict[str, Any]]:
    settings = load_settings()
    with database.connection(settings.database_url) as conn:
        database.initialize(conn)
        rows = database.list_predictions(conn, series)
    return [_row_to_dict(row) for row in rows]


@app.get("/predictions/latest")
def latest_prediction(series: str = Query(default="WCESTUS1")) -> dict[str, Any]:
    settings = load_settings()
    with database.connection(settings.database_url) as conn:
        database.initialize(conn)
        row = database.latest_prediction(conn, series)
    if row is None:
        raise HTTPException(status_code=404, detail="No prediction found")
    return _row_to_dict(row)
