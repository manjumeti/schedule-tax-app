"""Unit tests for the market-data provider abstraction."""
from datetime import date
from decimal import Decimal

import pytest

from app.core.exceptions import MarketDataUnavailableError
from app.domain.engine.market_data import (
    CsvSbiMarketDataProvider,
    ManualMarketDataProvider,
    build_market_data_provider,
)


def _write_year_csv(tmp_path, year: int, rows: dict[str, dict[str, str]]) -> None:
    currencies = sorted({c for row in rows.values() for c in row})
    year_dir = tmp_path / str(year)
    year_dir.mkdir()
    csv_path = year_dir / "sbi_tt_buy_rates.csv"
    header = ",".join(["DATE", *currencies])
    lines = [header]
    for date_str, row in sorted(rows.items()):
        lines.append(",".join([date_str, *(row.get(c, "") for c in currencies)]))
    csv_path.write_text("\n".join(lines) + "\n")


def test_manual_provider_always_requires_explicit_rate():
    provider = ManualMarketDataProvider()
    with pytest.raises(MarketDataUnavailableError):
        provider.get_fx_rate("USD", date(2024, 1, 1))


def test_build_market_data_provider_returns_manual_by_default():
    provider = build_market_data_provider("manual", sbi_rates_csv_dir="unused")
    assert isinstance(provider, ManualMarketDataProvider)


def test_build_market_data_provider_returns_csv_sbi(tmp_path):
    provider = build_market_data_provider("yfinance_sbi", sbi_rates_csv_dir=str(tmp_path))
    assert isinstance(provider, CsvSbiMarketDataProvider)


def test_csv_sbi_provider_returns_exact_date_rate(tmp_path):
    _write_year_csv(tmp_path, 2024, {"2024-01-01": {"USD": "83.12", "EUR": "91.5"}})
    provider = CsvSbiMarketDataProvider(csv_dir=str(tmp_path))

    assert provider.get_fx_rate("USD", date(2024, 1, 1)) == Decimal("83.12")
    assert provider.get_fx_rate("eur", date(2024, 1, 1)) == Decimal("91.5")


def test_csv_sbi_provider_falls_back_to_nearest_date(tmp_path):
    _write_year_csv(tmp_path, 2024, {"2024-01-03": {"USD": "83.5"}})
    provider = CsvSbiMarketDataProvider(csv_dir=str(tmp_path))

    assert provider.get_fx_rate("USD", date(2024, 1, 4)) == Decimal("83.5")


def test_csv_sbi_provider_skips_zero_rate_rows(tmp_path):
    _write_year_csv(
        tmp_path,
        2024,
        {
            "2024-01-01": {"CNY": "0"},
            "2024-01-02": {"CNY": "6.9"},
        },
    )
    provider = CsvSbiMarketDataProvider(csv_dir=str(tmp_path))

    assert provider.get_fx_rate("CNY", date(2024, 1, 1)) == Decimal("6.9")


def test_csv_sbi_provider_raises_when_no_data_found(tmp_path):
    provider = CsvSbiMarketDataProvider(csv_dir=str(tmp_path), max_days_search=1)
    with pytest.raises(MarketDataUnavailableError):
        provider.get_fx_rate("USD", date(2024, 1, 1))
