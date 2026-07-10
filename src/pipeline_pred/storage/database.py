from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from pipeline_pred.config import mysql_config_from_url, sqlite_path_from_url
from pipeline_pred.ingest.eia import EiaObservation


SQLITE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS observations (
    series TEXT NOT NULL,
    period DATE NOT NULL,
    value REAL NOT NULL,
    units TEXT NOT NULL,
    source TEXT NOT NULL,
    raw_json TEXT,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY (series, period)
);

CREATE TABLE IF NOT EXISTS market_prices (
    series TEXT NOT NULL,
    period DATE NOT NULL,
    value REAL NOT NULL,
    units TEXT NOT NULL,
    source TEXT NOT NULL,
    raw_json TEXT,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY (series, period)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series TEXT NOT NULL,
    target_period DATE NOT NULL,
    prediction REAL NOT NULL,
    actual REAL,
    value_error REAL,
    error_rate REAL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    source_data_through_period DATE NOT NULL,
    UNIQUE (series, target_period, model_name, model_version)
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    evaluated_at TEXT NOT NULL,
    source_data_through_period DATE NOT NULL
);
"""

MYSQL_SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS observations (
        series VARCHAR(64) NOT NULL,
        period DATE NOT NULL,
        `value` DOUBLE NOT NULL,
        units VARCHAR(32) NOT NULL,
        source VARCHAR(64) NOT NULL,
        raw_json LONGTEXT,
        fetched_at VARCHAR(40) NOT NULL,
        PRIMARY KEY (series, period)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS market_prices (
        series VARCHAR(64) NOT NULL,
        period DATE NOT NULL,
        `value` DOUBLE NOT NULL,
        units VARCHAR(32) NOT NULL,
        source VARCHAR(64) NOT NULL,
        raw_json LONGTEXT,
        fetched_at VARCHAR(40) NOT NULL,
        PRIMARY KEY (series, period)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        series VARCHAR(64) NOT NULL,
        target_period DATE NOT NULL,
        prediction DOUBLE NOT NULL,
        actual DOUBLE,
        value_error DOUBLE,
        error_rate DOUBLE,
        model_name VARCHAR(128) NOT NULL,
        model_version VARCHAR(64) NOT NULL,
        created_at VARCHAR(40) NOT NULL,
        source_data_through_period DATE NOT NULL,
        UNIQUE KEY uq_prediction_model (
            series, target_period, model_name, model_version
        )
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS model_metrics (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        series VARCHAR(64) NOT NULL,
        model_name VARCHAR(128) NOT NULL,
        model_version VARCHAR(64) NOT NULL,
        metric_name VARCHAR(128) NOT NULL,
        metric_value DOUBLE NOT NULL,
        evaluated_at VARCHAR(40) NOT NULL,
        source_data_through_period DATE NOT NULL
    )
    """,
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_mysql_connection(conn: Any) -> bool:
    return conn.__class__.__module__.startswith("mysql.connector")


def placeholder(conn: Any) -> str:
    return "%s" if is_mysql_connection(conn) else "?"


def connect(database_url: str) -> Any:
    if database_url.startswith(("mysql://", "mysql+mysqlconnector://")):
        import mysql.connector

        return mysql.connector.connect(**mysql_config_from_url(database_url))

    db_path = sqlite_path_from_url(database_url)
    if str(db_path) != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection(database_url: str) -> Iterator[Any]:
    conn = connect(database_url)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize(conn: Any) -> None:
    if is_mysql_connection(conn):
        cursor = conn.cursor()
        try:
            for statement in MYSQL_SCHEMA_STATEMENTS:
                cursor.execute(statement)
        finally:
            cursor.close()
        return
    conn.executescript(SQLITE_SCHEMA_SQL)


def upsert_observations(
    conn: Any,
    observations: list[EiaObservation],
    table: str = "observations",
    source: str = "eia_api_v2",
) -> int:
    if table not in {"observations", "market_prices"}:
        raise ValueError("table must be observations or market_prices")
    fetched_at = utc_now_iso()
    rows = [
        (
            obs.series,
            obs.period.isoformat(),
            obs.value,
            obs.units,
            source,
            json.dumps(obs.source_payload, sort_keys=True),
            fetched_at,
        )
        for obs in observations
    ]
    if is_mysql_connection(conn):
        cursor = conn.cursor()
        try:
            cursor.executemany(
                f"""
                INSERT INTO {table}
                    (series, period, `value`, units, source, raw_json, fetched_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    `value` = VALUES(`value`),
                    units = VALUES(units),
                    source = VALUES(source),
                    raw_json = VALUES(raw_json),
                    fetched_at = VALUES(fetched_at)
                """,
                rows,
            )
        finally:
            cursor.close()
    else:
        conn.executemany(
            f"""
            INSERT INTO {table}
                (series, period, value, units, source, raw_json, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(series, period) DO UPDATE SET
                value = excluded.value,
                units = excluded.units,
                source = excluded.source,
                raw_json = excluded.raw_json,
                fetched_at = excluded.fetched_at
            """,
            rows,
        )
    return len(rows)


def get_series(conn: Any, table: str, series: str) -> list[Any]:
    if table not in {"observations", "market_prices"}:
        raise ValueError("table must be observations or market_prices")
    sql = f"""
        SELECT series, period, `value` AS value, units, source, fetched_at
        FROM {table}
        WHERE series = {placeholder(conn)}
        ORDER BY period ASC
        """
    if is_mysql_connection(conn):
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (series,))
            return cursor.fetchall()
        finally:
            cursor.close()
    return conn.execute(sql, (series,)).fetchall()


def upsert_prediction(
    conn: Any,
    *,
    series: str,
    target_period: date,
    prediction: float,
    actual: float | None,
    model_name: str,
    model_version: str,
    source_data_through_period: date,
) -> None:
    value_error = None
    error_rate = None
    if actual not in (None, 0):
        value_error = prediction - actual
        error_rate = value_error / actual

    params = (
        series,
        target_period.isoformat(),
        prediction,
        actual,
        value_error,
        error_rate,
        model_name,
        model_version,
        utc_now_iso(),
        source_data_through_period.isoformat(),
    )
    if is_mysql_connection(conn):
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO predictions (
                    series, target_period, prediction, actual, value_error,
                    error_rate, model_name, model_version, created_at,
                    source_data_through_period
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    prediction = VALUES(prediction),
                    actual = VALUES(actual),
                    value_error = VALUES(value_error),
                    error_rate = VALUES(error_rate),
                    created_at = VALUES(created_at),
                    source_data_through_period = VALUES(source_data_through_period)
                """,
                params,
            )
        finally:
            cursor.close()
    else:
        conn.execute(
            """
            INSERT INTO predictions (
                series, target_period, prediction, actual, value_error, error_rate,
                model_name, model_version, created_at, source_data_through_period
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(series, target_period, model_name, model_version) DO UPDATE SET
                prediction = excluded.prediction,
                actual = excluded.actual,
                value_error = excluded.value_error,
                error_rate = excluded.error_rate,
                created_at = excluded.created_at,
                source_data_through_period = excluded.source_data_through_period
            """,
            params,
        )


def insert_metrics(
    conn: Any,
    *,
    series: str,
    model_name: str,
    model_version: str,
    metrics: dict[str, float],
    source_data_through_period: date,
) -> None:
    evaluated_at = utc_now_iso()
    rows = [
        (
            series,
            model_name,
            model_version,
            name,
            value,
            evaluated_at,
            source_data_through_period.isoformat(),
        )
        for name, value in metrics.items()
    ]
    if is_mysql_connection(conn):
        cursor = conn.cursor()
        try:
            cursor.executemany(
                """
                INSERT INTO model_metrics (
                    series, model_name, model_version, metric_name, metric_value,
                    evaluated_at, source_data_through_period
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
        finally:
            cursor.close()
        return
    conn.executemany(
        """
        INSERT INTO model_metrics (
            series, model_name, model_version, metric_name, metric_value,
            evaluated_at, source_data_through_period
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def list_predictions(conn: Any, series: str) -> list[Any]:
    sql = f"""
        SELECT series, target_period, prediction, actual, value_error, error_rate,
               model_name, model_version, created_at, source_data_through_period
        FROM predictions
        WHERE series = {placeholder(conn)}
        ORDER BY target_period ASC
        """
    if is_mysql_connection(conn):
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (series,))
            return cursor.fetchall()
        finally:
            cursor.close()
    return conn.execute(sql, (series,)).fetchall()


def latest_prediction(conn: Any, series: str) -> Any | None:
    sql = f"""
        SELECT series, target_period, prediction, actual, value_error, error_rate,
               model_name, model_version, created_at, source_data_through_period
        FROM predictions
        WHERE series = {placeholder(conn)}
        ORDER BY target_period DESC, created_at DESC
        LIMIT 1
        """
    if is_mysql_connection(conn):
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (series,))
            return cursor.fetchone()
        finally:
            cursor.close()
    return conn.execute(sql, (series,)).fetchone()


def database_exists(database_url: str) -> bool:
    if database_url.startswith(("mysql://", "mysql+mysqlconnector://")):
        try:
            conn = connect(database_url)
            conn.close()
            return True
        except Exception:
            return False
    db_path = sqlite_path_from_url(database_url)
    return str(db_path) == ":memory:" or Path(db_path).exists()
