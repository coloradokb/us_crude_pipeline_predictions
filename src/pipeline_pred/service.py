from __future__ import annotations

from dataclasses import dataclass

from pipeline_pred.config import Settings
from pipeline_pred.features.build import build_training_frame
from pipeline_pred.ingest.eia import EiaClient
from pipeline_pred.models.baseline import forecast_next_week, forecast_recent_history
from pipeline_pred.storage import database


@dataclass(frozen=True)
class IngestResult:
    observations: int
    market_prices: int


def initialize_database(settings: Settings) -> None:
    with database.connection(settings.database_url) as conn:
        database.initialize(conn)


def ingest_eia(settings: Settings, start: str = "2015-01-01") -> IngestResult:
    client = EiaClient(
        settings.eia_api_key,
        timeout_seconds=settings.request_timeout_seconds,
    )
    weekly_stocks = client.fetch_weekly_stocks(start=start)
    wti_spot = client.fetch_daily_wti_spot(start=start)
    with database.connection(settings.database_url) as conn:
        database.initialize(conn)
        obs_count = database.upsert_observations(conn, weekly_stocks, "observations")
        price_count = database.upsert_observations(conn, wti_spot, "market_prices")
    return IngestResult(observations=obs_count, market_prices=price_count)


def generate_prediction(settings: Settings, series: str = "WCESTUS1") -> dict[str, object]:
    with database.connection(settings.database_url) as conn:
        database.initialize(conn)
        observations = database.get_series(conn, "observations", series)
        prices = database.get_series(conn, "market_prices", "RWTC")
        frame = build_training_frame(observations, prices)
        result = forecast_next_week(frame)
        database.upsert_prediction(
            conn,
            series=series,
            target_period=result.target_period.date(),
            prediction=result.prediction,
            actual=result.actual,
            model_name=result.model_name,
            model_version=result.model_version,
            source_data_through_period=result.source_data_through_period.date(),
        )
        if result.metrics:
            database.insert_metrics(
                conn,
                series=series,
                model_name=result.model_name,
                model_version=result.model_version,
                metrics=result.metrics,
                source_data_through_period=result.source_data_through_period.date(),
            )
    return {
        "series": series,
        "target_period": result.target_period.date().isoformat(),
        "prediction": result.prediction,
        "model_name": result.model_name,
        "model_version": result.model_version,
        "source_data_through_period": result.source_data_through_period.date().isoformat(),
        "metrics": result.metrics,
    }


def backfill_recent_predictions(
    settings: Settings,
    series: str = "WCESTUS1",
    weeks: int = 9,
) -> list[dict[str, object]]:
    with database.connection(settings.database_url) as conn:
        database.initialize(conn)
        observations = database.get_series(conn, "observations", series)
        prices = database.get_series(conn, "market_prices", "RWTC")
        frame = build_training_frame(observations, prices)
        results = forecast_recent_history(frame, weeks=weeks)
        for result in results:
            database.upsert_prediction(
                conn,
                series=series,
                target_period=result.target_period.date(),
                prediction=result.prediction,
                actual=result.actual,
                model_name=result.model_name,
                model_version=result.model_version,
                source_data_through_period=result.source_data_through_period.date(),
            )

    return [
        {
            "series": series,
            "target_period": result.target_period.date().isoformat(),
            "prediction": result.prediction,
            "actual": result.actual,
            "model_name": result.model_name,
            "model_version": result.model_version,
            "source_data_through_period": result.source_data_through_period.date().isoformat(),
        }
        for result in results
    ]
