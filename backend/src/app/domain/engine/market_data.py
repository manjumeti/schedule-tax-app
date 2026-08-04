"""Market data / FX rate lookup, ported from the existing `itr` repository.

This isolates the *only* piece of the original calculation script that
performs I/O (PDF parsing of SBI reference rates, Yahoo Finance calls) behind
a small Protocol, so the rest of the engine stays pure and testable, and so
this provider can be swapped (e.g. for a paid FX-rate API) without touching
callers.

The core formula reused from `itr/src/generate_schedule_fa_a3.py::get_sbi_tt_rate`
is preserved: locate the PDF for the SBI reference-rate publication date
closest to the requested date (searching backwards first) and extract the
USD TT buying rate.
"""
import os
import re
from datetime import date, timedelta
from decimal import Decimal
from typing import Protocol

from app.core.exceptions import MarketDataUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)


class MarketDataProvider(Protocol):
    """Contract for looking up a foreign-exchange rate for a given date."""

    def get_fx_rate(self, currency: str, on_date: date) -> Decimal: ...


class ManualMarketDataProvider:
    """Default provider: the caller always supplies the exchange rate explicitly.

    Used when `market_data_provider=manual` (the safe default for a web app that
    should not perform outbound network/file-system calls per calculation request).
    """

    def get_fx_rate(self, currency: str, on_date: date) -> Decimal:
        raise MarketDataUnavailableError(
            "Automatic FX rate lookup is disabled; supply exchange_rate explicitly.",
            details={"currency": currency, "date": on_date.isoformat()},
        )


class YfinanceSbiMarketDataProvider:
    """Looks up the SBI TT buying rate from the locally mirrored PDF archive.

    Ported from `get_sbi_tt_rate` in the existing `itr` repository, with prints
    replaced by structured logging and exceptions instead of returning None.
    """

    def __init__(self, pdf_dir: str, max_days_search: int = 7) -> None:
        self._pdf_dir = pdf_dir
        self._max_days_search = max_days_search
        self._cache: dict[tuple[str, date], Decimal] = {}

    def get_fx_rate(self, currency: str, on_date: date) -> Decimal:
        if currency.upper() != "USD":
            raise MarketDataUnavailableError(
                f"SBI PDF archive only supports USD rates, got {currency}"
            )

        cache_key = (currency.upper(), on_date)
        if cache_key in self._cache:
            return self._cache[cache_key]

        rate = self._lookup_rate_near_date(on_date)
        if rate is None:
            raise MarketDataUnavailableError(
                f"No SBI reference rate found within {self._max_days_search} days of "
                f"{on_date.isoformat()}"
            )
        self._cache[cache_key] = rate
        return rate

    def _lookup_rate_near_date(self, target_date: date) -> Decimal | None:
        import pypdf

        for day_offset in range(self._max_days_search + 1):
            for direction in (-1, 1):
                if day_offset == 0 and direction == 1:
                    continue
                check_date = target_date + timedelta(days=day_offset * direction)
                pdf_path = os.path.join(
                    self._pdf_dir,
                    str(check_date.year),
                    str(check_date.month),
                    f"{check_date.isoformat()}.pdf",
                )
                if not os.path.exists(pdf_path):
                    continue
                try:
                    with open(pdf_path, "rb") as fh:
                        reader = pypdf.PdfReader(fh)
                        text = "".join(page.extract_text() for page in reader.pages)
                    match = re.search(r"USD.*?(\d+\.\d+)", text)
                    if match:
                        logger.info(
                            "sbi_rate_found",
                            requested_date=target_date.isoformat(),
                            matched_date=check_date.isoformat(),
                        )
                        return Decimal(match.group(1))
                except Exception:  # noqa: BLE001 - degrade to "not found", logged below
                    logger.warning("sbi_pdf_parse_failed", path=pdf_path, exc_info=True)
        return None


def build_market_data_provider(
    provider: str, sbi_pdf_dir: str
) -> MarketDataProvider:
    if provider == "yfinance_sbi":
        return YfinanceSbiMarketDataProvider(pdf_dir=sbi_pdf_dir)
    return ManualMarketDataProvider()


class StockPriceProvider(Protocol):
    """Contract for looking up a ticker's peak/closing price within a calendar year."""

    def get_peak_and_closing(
        self, ticker: str, year: int
    ) -> tuple[date, Decimal, date, Decimal]:
        """Returns (peak_date, peak_price, closing_date, closing_price)."""
        ...


class ManualStockPriceProvider:
    """Default provider: refuses automatic lookups (no outbound calls per request)."""

    def get_peak_and_closing(
        self, ticker: str, year: int
    ) -> tuple[date, Decimal, date, Decimal]:
        raise MarketDataUnavailableError(
            "Automatic stock price lookup is disabled; set "
            "APP_MARKET_DATA_PROVIDER=yfinance_sbi to enable RSU/ESPP lot-based Form A3.",
            details={"ticker": ticker, "year": year},
        )


class YfinanceStockPriceProvider:
    """Looks up peak/closing close price for a ticker/year via Yahoo Finance.

    Ported from `get_stock_prices` + `calculate_peak_and_closing` in the
    existing `itr` repository's `generate_schedule_fa_a3.py`.
    """

    def __init__(self) -> None:
        self._cache: dict[tuple[str, int], tuple[date, Decimal, date, Decimal]] = {}

    def get_peak_and_closing(
        self, ticker: str, year: int
    ) -> tuple[date, Decimal, date, Decimal]:
        cache_key = (ticker.upper(), year)
        if cache_key in self._cache:
            return self._cache[cache_key]

        import yfinance as yf

        stock = yf.Ticker(ticker)
        history = stock.history(start=f"{year}-01-01", end=f"{year}-12-31")
        if history.empty:
            raise MarketDataUnavailableError(
                f"No stock price history found for {ticker} in {year}"
            )

        peak_date = history["Close"].idxmax()
        peak_price = Decimal(str(history.loc[peak_date, "Close"]))
        closing_date = history.index[-1]
        closing_price = Decimal(str(history.loc[closing_date, "Close"]))

        result = (
            peak_date.to_pydatetime().date(),
            peak_price,
            closing_date.to_pydatetime().date(),
            closing_price,
        )
        self._cache[cache_key] = result
        return result


def build_stock_price_provider(provider: str) -> StockPriceProvider:
    if provider == "yfinance_sbi":
        return YfinanceStockPriceProvider()
    return ManualStockPriceProvider()

