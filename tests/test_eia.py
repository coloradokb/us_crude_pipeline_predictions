from datetime import date

import pytest

from pipeline_pred.ingest.eia import EiaApiError, normalize_eia_rows


def test_normalize_eia_rows_converts_strings_to_typed_values():
    rows = [
        {
            "period": "2026-07-03",
            "series": "WCESTUS1",
            "value": "411357",
            "units": "MBBL",
        }
    ]

    result = normalize_eia_rows(rows)

    assert result[0].series == "WCESTUS1"
    assert result[0].period == date(2026, 7, 3)
    assert result[0].value == 411357.0
    assert result[0].units == "MBBL"


def test_normalize_eia_rows_rejects_bad_rows():
    with pytest.raises(EiaApiError):
        normalize_eia_rows([{"period": "bad"}])
