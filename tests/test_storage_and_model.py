from datetime import date, timedelta

import pandas as pd

from pipeline_pred.features.build import build_training_frame
from pipeline_pred.ingest.eia import EiaObservation
from pipeline_pred.models.baseline import forecast_next_week, forecast_recent_history
from pipeline_pred.storage import database


def _obs(series: str, period: date, value: float, units: str = "MBBL") -> EiaObservation:
    return EiaObservation(
        series=series,
        period=period,
        value=value,
        units=units,
        source_payload={"series": series, "period": period.isoformat(), "value": str(value)},
    )


def test_upsert_observations_updates_existing_row():
    conn = database.connect(":memory:")
    database.initialize(conn)
    period = date(2026, 7, 3)

    database.upsert_observations(conn, [_obs("WCESTUS1", period, 411357)])
    database.upsert_observations(conn, [_obs("WCESTUS1", period, 411358)])

    rows = database.get_series(conn, "observations", "WCESTUS1")
    assert len(rows) == 1
    assert rows[0]["value"] == 411358


def test_build_training_frame_and_forecast_next_week():
    start = date(2024, 1, 5)
    observations = [
        _obs("WCESTUS1", start + timedelta(days=7 * idx), 400000 + idx * 100)
        for idx in range(70)
    ]
    prices = []
    for day in range(490):
        period = start + timedelta(days=day)
        prices.append(_obs("RWTC", period, 70 + day * 0.01, "$/BBL"))

    frame = build_training_frame(
        [{"period": obs.period.isoformat(), "value": obs.value} for obs in observations],
        [{"period": obs.period.isoformat(), "value": obs.value} for obs in prices],
    )
    result = forecast_next_week(frame)

    assert isinstance(frame, pd.DataFrame)
    assert result.target_period.date() == start + timedelta(days=7 * 70)
    assert result.prediction > 0
    assert "mae" in result.metrics


def test_forecast_recent_history_sets_known_actuals():
    start = date(2024, 1, 5)
    observations = [
        _obs("WCESTUS1", start + timedelta(days=7 * idx), 400000 + idx * 100)
        for idx in range(70)
    ]
    prices = [
        _obs("RWTC", start + timedelta(days=day), 70 + day * 0.01, "$/BBL")
        for day in range(490)
    ]
    frame = build_training_frame(
        [{"period": obs.period.isoformat(), "value": obs.value} for obs in observations],
        [{"period": obs.period.isoformat(), "value": obs.value} for obs in prices],
    )

    results = forecast_recent_history(frame, weeks=3)

    assert len(results) == 3
    assert results[-1].target_period.date() == start + timedelta(days=7 * 69)
    assert results[-1].actual == 406900


def test_prediction_upsert_stores_actual_error_fields():
    conn = database.connect(":memory:")
    database.initialize(conn)

    database.upsert_prediction(
        conn,
        series="WCESTUS1",
        target_period=date(2026, 7, 3),
        prediction=410000,
        actual=411000,
        model_name="ridge_lag_wti",
        model_version="0.1.0",
        source_data_through_period=date(2026, 6, 26),
    )

    row = database.latest_prediction(conn, "WCESTUS1")
    assert row["actual"] == 411000
    assert row["value_error"] == -1000
    assert round(row["error_rate"], 6) == round(-1000 / 411000, 6)
