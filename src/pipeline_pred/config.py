from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus, unquote_plus, urlparse

from dotenv import load_dotenv


DEFAULT_DB_PATH = Path("data/pipeline_predictions.sqlite3")


@dataclass(frozen=True)
class Settings:
    eia_api_key: str | None
    database_url: str
    log_level: str
    app_env: str
    request_timeout_seconds: int
    api_cors_origins: list[str]


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        eia_api_key=os.getenv("EIA_API_KEY"),
        database_url=_database_url_from_env(),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        app_env=os.getenv("APP_ENV", "local"),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        api_cors_origins=_list_from_env(
            "API_CORS_ORIGINS",
            "http://localhost:8561,http://127.0.0.1:8561",
        ),
    )


def _list_from_env(name: str, default: str) -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _database_url_from_env() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    mysql_host = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST")
    mysql_db = os.getenv("MYSQL_DB") or os.getenv("DB_DATABASE")
    mysql_user = os.getenv("MYSQL_USER") or os.getenv("DB_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    if mysql_host and mysql_db and mysql_user:
        password_part = f":{quote_plus(mysql_password)}" if mysql_password else ""
        return (
            f"mysql://{quote_plus(mysql_user)}{password_part}"
            f"@{mysql_host}:{mysql_port}/{mysql_db}"
        )

    return f"sqlite:///{DEFAULT_DB_PATH}"


def sqlite_path_from_url(database_url: str) -> Path:
    if database_url == ":memory:":
        return Path(database_url)
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError(
            "Only sqlite:/// DATABASE_URL values are supported by the new local runtime."
        )
    return Path(database_url[len(prefix) :])


def mysql_config_from_url(database_url: str) -> dict[str, str | int]:
    parsed = urlparse(database_url)
    if parsed.scheme not in {"mysql", "mysql+mysqlconnector"}:
        raise ValueError("Expected mysql:// or mysql+mysqlconnector:// DATABASE_URL")
    if not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError("MySQL DATABASE_URL must include host and database name")
    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "database": unquote_plus(parsed.path.strip("/")),
        "user": unquote_plus(parsed.username or ""),
        "password": unquote_plus(parsed.password or ""),
    }
