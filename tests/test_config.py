from pipeline_pred.config import load_settings, mysql_config_from_url


def test_load_settings_builds_mysql_url_from_split_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MYSQL_HOST", "db.example.test")
    monkeypatch.setenv("MYSQL_PORT", "3307")
    monkeypatch.setenv("MYSQL_DB", "pipeline")
    monkeypatch.setenv("MYSQL_USER", "model_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")

    settings = load_settings()

    assert settings.database_url == (
        "mysql://model_user:secret@db.example.test:3307/pipeline"
    )
    assert "http://localhost:8561" in settings.api_cors_origins


def test_mysql_config_from_url_decodes_credentials():
    config = mysql_config_from_url(
        "mysql://model_user:p%40ss%2Bword@db.example.test:3307/pipeline"
    )

    assert config["user"] == "model_user"
    assert config["password"] == "p@ss+word"
    assert config["database"] == "pipeline"
