from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


MODEL_NAME = "ridge_lag_wti"
MODEL_VERSION = "0.1.0"
FEATURE_COLUMNS = [
    "lag_1",
    "lag_2",
    "lag_4",
    "change_1",
    "rolling_4_mean",
    "rolling_8_mean",
    "wti_week_avg",
    "wti_week_last",
]


@dataclass(frozen=True)
class PredictionResult:
    target_period: pd.Timestamp
    prediction: float
    actual: float | None
    source_data_through_period: pd.Timestamp
    metrics: dict[str, float]
    model_name: str = MODEL_NAME
    model_version: str = MODEL_VERSION


def forecast_next_week(feature_frame: pd.DataFrame) -> PredictionResult:
    train = feature_frame.dropna(subset=FEATURE_COLUMNS + ["y"]).copy()
    if train.empty:
        raise ValueError("Not enough complete rows to train a model")

    model = _fit_model(train)
    latest = feature_frame.iloc[-1:].copy()
    next_row = _make_next_feature_row(feature_frame)
    prediction = float(model.predict(next_row[FEATURE_COLUMNS])[0])
    metrics = walk_forward_metrics(train)

    return PredictionResult(
        target_period=next_row["period"].iloc[0],
        prediction=round(prediction),
        actual=None,
        source_data_through_period=latest["period"].iloc[0],
        metrics=metrics,
    )


def forecast_recent_history(
    feature_frame: pd.DataFrame,
    weeks: int,
) -> list[PredictionResult]:
    """Generate leakage-safe one-week forecasts for recent observed periods."""
    df = feature_frame.sort_values("period").reset_index(drop=True)
    complete = df.dropna(subset=FEATURE_COLUMNS + ["y"]).copy()
    if complete.empty:
        raise ValueError("Not enough complete rows to train a model")

    target_periods = list(complete["period"].tail(weeks))
    results: list[PredictionResult] = []
    for target_period in target_periods:
        history = df[df["period"] < target_period].copy()
        train = history.dropna(subset=FEATURE_COLUMNS + ["y"]).copy()
        if train.empty:
            continue

        model = _fit_model(train)
        next_row = _make_next_feature_row(history)
        if next_row["period"].iloc[0] != target_period:
            continue
        prediction = float(model.predict(next_row[FEATURE_COLUMNS])[0])
        actual = float(df.loc[df["period"] == target_period, "y"].iloc[0])
        results.append(
            PredictionResult(
                target_period=target_period,
                prediction=round(prediction),
                actual=actual,
                source_data_through_period=history["period"].iloc[-1],
                metrics={},
            )
        )
    return results


def _fit_model(train: pd.DataFrame) -> Pipeline:
    model = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("ridge", Ridge(alpha=1.0)),
        ]
    )
    model.fit(train[FEATURE_COLUMNS], train["y"])
    return model


def _make_next_feature_row(feature_frame: pd.DataFrame) -> pd.DataFrame:
    df = feature_frame.sort_values("period").reset_index(drop=True)
    last = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else last
    row = {
        "period": last["period"] + pd.Timedelta(days=7),
        "lag_1": last["y"],
        "lag_2": previous["y"],
        "lag_4": df.iloc[-4]["y"] if len(df) >= 4 else last["y"],
        "change_1": last["y"] - previous["y"],
        "rolling_4_mean": df.tail(4)["y"].mean(),
        "rolling_8_mean": df.tail(8)["y"].mean(),
        "wti_week_avg": last.get("wti_week_avg"),
        "wti_week_last": last.get("wti_week_last"),
    }
    return pd.DataFrame([row])


def walk_forward_metrics(train: pd.DataFrame, min_train_rows: int = 52) -> dict[str, float]:
    if len(train) <= min_train_rows + 4:
        return {}

    predictions = []
    actuals = []
    naive_predictions = []
    for idx in range(min_train_rows, len(train)):
        history = train.iloc[:idx]
        target = train.iloc[idx]
        model = _fit_model(history)
        pred = float(model.predict(target[FEATURE_COLUMNS].to_frame().T)[0])
        predictions.append(pred)
        actuals.append(float(target["y"]))
        naive_predictions.append(float(target["lag_1"]))

    errors = [pred - actual for pred, actual in zip(predictions, actuals)]
    naive_errors = [
        pred - actual for pred, actual in zip(naive_predictions, actuals)
    ]
    absolute_percentage_errors = [
        abs(error) / actual for error, actual in zip(errors, actuals) if actual
    ]
    return {
        "mae": float(sum(abs(error) for error in errors) / len(errors)),
        "rmse": float(sqrt(sum(error**2 for error in errors) / len(errors))),
        "mape": float(
            sum(absolute_percentage_errors) / len(absolute_percentage_errors)
        ),
        "naive_mae": float(
            sum(abs(error) for error in naive_errors) / len(naive_errors)
        ),
    }
