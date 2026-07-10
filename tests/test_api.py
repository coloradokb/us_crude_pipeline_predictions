from datetime import date

from pipeline_pred.api.main import latest_prediction, observations
from pipeline_pred.ingest.eia import EiaObservation
from pipeline_pred.storage import database


def test_prediction_endpoints(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    conn = database.connect(f"sqlite:///{db_path}")
    database.initialize(conn)
    obs = EiaObservation(
        series="WCESTUS1",
        period=date(2026, 7, 3),
        value=411357,
        units="MBBL",
        source_payload={},
    )
    database.upsert_observations(conn, [obs])
    database.upsert_prediction(
        conn,
        series="WCESTUS1",
        target_period=date(2026, 7, 10),
        prediction=412000,
        actual=None,
        model_name="ridge_lag_wti",
        model_version="0.1.0",
        source_data_through_period=date(2026, 7, 3),
    )
    conn.commit()
    conn.close()

    latest = latest_prediction("WCESTUS1")
    observed = observations("WCESTUS1")

    assert latest["target_period"] == "2026-07-10"
    assert observed[0]["value"] == 411357
