from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

import requests


EIA_BASE_URL = "https://api.eia.gov/v2"
WCESTUS1_ROUTE = "/petroleum/stoc/wstk/data/"
WTI_SPOT_ROUTE = "/petroleum/pri/spt/data/"


@dataclass(frozen=True)
class EiaObservation:
    series: str
    period: date
    value: float
    units: str
    source_payload: dict[str, Any]


class EiaApiError(RuntimeError):
    """Raised when EIA returns an unusable response."""


class EiaClient:
    def __init__(
        self,
        api_key: str | None,
        base_url: str = EIA_BASE_URL,
        timeout_seconds: int = 30,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def fetch_weekly_stocks(
        self,
        series: str = "WCESTUS1",
        start: str | None = None,
        end: str | None = None,
    ) -> list[EiaObservation]:
        return self._fetch_series(
            route=WCESTUS1_ROUTE,
            frequency="weekly",
            series=series,
            start=start,
            end=end,
        )

    def fetch_daily_wti_spot(
        self,
        series: str = "RWTC",
        start: str | None = None,
        end: str | None = None,
    ) -> list[EiaObservation]:
        return self._fetch_series(
            route=WTI_SPOT_ROUTE,
            frequency="daily",
            series=series,
            start=start,
            end=end,
        )

    def _fetch_series(
        self,
        route: str,
        frequency: str,
        series: str,
        start: str | None,
        end: str | None,
    ) -> list[EiaObservation]:
        rows: list[dict[str, Any]] = []
        offset = 0
        page_size = 5000

        while True:
            params: list[tuple[str, str | int]] = [
                ("frequency", frequency),
                ("data[0]", "value"),
                ("facets[series][]", series),
                ("sort[0][column]", "period"),
                ("sort[0][direction]", "asc"),
                ("offset", offset),
                ("length", page_size),
            ]
            if self.api_key:
                params.append(("api_key", self.api_key))
            if start:
                params.append(("start", start))
            if end:
                params.append(("end", end))

            payload = self._get(route, params)
            response = payload.get("response", {})
            page = response.get("data", [])
            if not isinstance(page, list):
                raise EiaApiError("EIA response data was not a list")
            rows.extend(page)

            total = int(response.get("total", len(rows)) or 0)
            if len(rows) >= total or len(page) == 0:
                break
            offset += page_size

        return normalize_eia_rows(rows)

    def _get(self, route: str, params: Iterable[tuple[str, str | int]]) -> dict[str, Any]:
        url = f"{self.base_url}{route}"
        response = self.session.get(url, params=list(params), timeout=self.timeout_seconds)
        if response.status_code >= 400:
            raise EiaApiError(f"EIA request failed: {response.status_code} {response.text}")
        payload = response.json()
        if "error" in payload:
            raise EiaApiError(str(payload["error"]))
        return payload


def normalize_eia_rows(rows: Iterable[dict[str, Any]]) -> list[EiaObservation]:
    observations: list[EiaObservation] = []
    for row in rows:
        try:
            observations.append(
                EiaObservation(
                    series=str(row["series"]),
                    period=date.fromisoformat(str(row["period"])),
                    value=float(row["value"]),
                    units=str(row.get("units", "")),
                    source_payload=dict(row),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise EiaApiError(f"Could not normalize EIA row: {row}") from exc
    return observations
