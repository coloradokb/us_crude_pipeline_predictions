from __future__ import annotations

from datetime import timedelta

import pandas as pd


def observations_to_frame(rows: list) -> pd.DataFrame:
    data = [{"period": row["period"], "value": row["value"]} for row in rows]
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["period", "y"])
    df["period"] = pd.to_datetime(df["period"])
    df["y"] = pd.to_numeric(df["value"])
    return df[["period", "y"]].sort_values("period").reset_index(drop=True)


def prices_to_weekly_frame(rows: list) -> pd.DataFrame:
    data = [{"period": row["period"], "value": row["value"]} for row in rows]
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["period", "wti_week_avg", "wti_week_last"])
    df["period"] = pd.to_datetime(df["period"])
    df["value"] = pd.to_numeric(df["value"])
    df = df.sort_values("period")

    weekly_rows = []
    first = df["period"].min().date()
    last = df["period"].max().date()
    current = first + timedelta(days=(4 - first.weekday()) % 7)
    while current <= last + timedelta(days=7):
        start = pd.Timestamp(current - timedelta(days=6))
        end = pd.Timestamp(current)
        window = df[(df["period"] >= start) & (df["period"] <= end)]
        if not window.empty:
            weekly_rows.append(
                {
                    "period": pd.Timestamp(current),
                    "wti_week_avg": float(window["value"].mean()),
                    "wti_week_last": float(window.iloc[-1]["value"]),
                }
            )
        current += timedelta(days=7)
    return pd.DataFrame(weekly_rows)


def build_training_frame(observations: list, prices: list) -> pd.DataFrame:
    target = observations_to_frame(observations)
    price_features = prices_to_weekly_frame(prices)
    if target.empty:
        return target
    df = target.merge(price_features, on="period", how="left")
    df["wti_week_avg"] = df["wti_week_avg"].ffill().bfill()
    df["wti_week_last"] = df["wti_week_last"].ffill().bfill()

    df["lag_1"] = df["y"].shift(1)
    df["lag_2"] = df["y"].shift(2)
    df["lag_4"] = df["y"].shift(4)
    df["change_1"] = df["y"].shift(1) - df["y"].shift(2)
    df["rolling_4_mean"] = df["y"].shift(1).rolling(4).mean()
    df["rolling_8_mean"] = df["y"].shift(1).rolling(8).mean()
    return df


def next_week_period(df: pd.DataFrame) -> pd.Timestamp:
    if df.empty:
        raise ValueError("Cannot infer next period from an empty dataframe")
    return df["period"].max() + pd.Timedelta(days=7)
