"""Unit tests for the market-data provider abstraction."""
import pytest

from app.core.exceptions import MarketDataUnavailableError
from app.domain.engine.market_data import (
    ManualMarketDataProvider,
    YfinanceSbiMarketDataProvider,
    build_market_data_provider,
)


def test_manual_provider_always_requires_explicit_rate():
    provider = ManualMarketDataProvider()
    with pytest.raises(MarketDataUnavailableError):
        provider.get_fx_rate("USD", __import__("datetime").date(2024, 1, 1))


def test_build_market_data_provider_returns_manual_by_default():
    provider = build_market_data_provider("manual", sbi_pdf_dir="unused")
    assert isinstance(provider, ManualMarketDataProvider)


def test_build_market_data_provider_returns_yfinance_sbi():
    provider = build_market_data_provider("yfinance_sbi", sbi_pdf_dir="/tmp/does-not-exist")
    assert isinstance(provider, YfinanceSbiMarketDataProvider)


def test_yfinance_sbi_provider_rejects_non_usd_currency():
    provider = YfinanceSbiMarketDataProvider(pdf_dir="/tmp/does-not-exist")
    with pytest.raises(MarketDataUnavailableError):
        provider.get_fx_rate("EUR", __import__("datetime").date(2024, 1, 1))


def test_yfinance_sbi_provider_raises_when_no_pdf_found():
    provider = YfinanceSbiMarketDataProvider(pdf_dir="/tmp/does-not-exist", max_days_search=1)
    with pytest.raises(MarketDataUnavailableError):
        provider.get_fx_rate("USD", __import__("datetime").date(2024, 1, 1))
