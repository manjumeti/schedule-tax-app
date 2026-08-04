"""Market data / FX rate lookup, ported from the existing `itr` repository.

This isolates the *only* piece of the original calculation script that
performs I/O (SBI reference rate lookup, Yahoo Finance calls) behind a small
Protocol, so the rest of the engine stays pure and testable, and so this
provider can be swapped (e.g. for a paid FX-rate API) without touching callers.

FX rates are read from the per-year "wide" CSVs produced by
`schedule-tax-app/scripts/extract_sbi_rates.py` (one row per date, one column
per currency's SBI TT BUY rate), which are kept up to date by the
`daily-sbi-rates` GitHub Action. The nearest-date search (backwards first)
mirrors `get_sbi_tt_rate` from `itr/src/generate_schedule_fa_a3.py`.
"""
import csv
import os
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
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


class CsvSbiMarketDataProvider:
    """Looks up the SBI TT BUY rate from the per-year CSVs in scripts/data/.

    Each CSV has one row per date and one column per currency (see
    `scripts/extract_sbi_rates.py`). A rate of 0 means SBI did not publish a
    card rate for that currency that day, so it is treated the same as a
    missing row when searching nearby dates.
    """

    def __init__(self, csv_dir: str, max_days_search: int = 7) -> None:
        self._csv_dir = csv_dir
        self._max_days_search = max_days_search
        self._year_cache: dict[int, dict[str, dict[str, str]]] = {}
        self._rate_cache: dict[tuple[str, date], Decimal] = {}

    def get_fx_rate(self, currency: str, on_date: date) -> Decimal:
        currency = currency.upper()
        cache_key = (currency, on_date)
        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]

        rate = self._lookup_rate_near_date(currency, on_date)
        if rate is None:
            raise MarketDataUnavailableError(
                f"No SBI TT BUY rate found for {currency} within "
                f"{self._max_days_search} days of {on_date.isoformat()}"
            )
        self._rate_cache[cache_key] = rate
        return rate

    def _load_year(self, year: int) -> dict[str, dict[str, str]]:
        if year not in self._year_cache:
            csv_path = os.path.join(self._csv_dir, str(year), "sbi_tt_buy_rates.csv")
            rows: dict[str, dict[str, str]] = {}
            if os.path.exists(csv_path):
                with open(csv_path, "r", encoding="utf-8", newline="") as fh:
                    for row in csv.DictReader(fh):
                        rows[row["DATE"]] = row
            self._year_cache[year] = rows
        return self._year_cache[year]

    def _candidate_dates(self, target_date: date):
        """Dates to try, nearest first, preferring earlier dates on ties."""
        for day_offset in range(self._max_days_search + 1):
            for direction in (-1, 1):
                if day_offset == 0 and direction == 1:
                    continue
                yield target_date + timedelta(days=day_offset * direction)

    def _rate_on(self, currency: str, on_date: date) -> Decimal | None:
        row = self._load_year(on_date.year).get(on_date.isoformat())
        raw_rate = row.get(currency) if row else None
        if not raw_rate:
            return None
        try:
            rate = Decimal(raw_rate)
        except InvalidOperation:
            return None
        return rate if rate > 0 else None  # 0 means SBI published no card rate that day

    def _lookup_rate_near_date(self, currency: str, target_date: date) -> Decimal | None:
        for check_date in self._candidate_dates(target_date):
            rate = self._rate_on(currency, check_date)
            if rate is not None:
                logger.info(
                    "sbi_rate_found",
                    currency=currency,
                    requested_date=target_date.isoformat(),
                    matched_date=check_date.isoformat(),
                )
                return rate
        return None


def build_market_data_provider(
    provider: str, sbi_rates_csv_dir: str
) -> MarketDataProvider:
    if provider == "yfinance_sbi":
        return CsvSbiMarketDataProvider(csv_dir=sbi_rates_csv_dir)
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

