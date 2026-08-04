"""Unit tests for lot-based Form A3 calculation (RSU/ESPP vest aggregation)."""
from datetime import date
from decimal import Decimal

import pytest

from app.domain.engine.itr_engine import ItrCalculationEngine
from app.dto.a3 import A3CalculateFromLotsRequest, A3HoldingRequest, A3LotRequest
from app.services.a3_service import A3Service


class _FakeFxProvider:
    """Returns a fixed rate per date so expected INR values are easy to assert."""

    def __init__(self, rates: dict[date, Decimal]) -> None:
        self._rates = rates

    def get_fx_rate(self, currency: str, on_date: date) -> Decimal:
        return self._rates[on_date]


class _FakeStockPriceProvider:
    def __init__(self, peak: tuple[date, Decimal], closing: tuple[date, Decimal]) -> None:
        self._peak = peak
        self._closing = closing

    def get_peak_and_closing(self, ticker: str, year: int):
        return (*self._peak, *self._closing)


@pytest.fixture
def service() -> A3Service:
    acquisition_date = date(2023, 6, 30)
    peak_date = date(2023, 12, 29)
    closing_date = date(2023, 12, 29)
    fx_provider = _FakeFxProvider(
        {
            acquisition_date: Decimal("82"),
            peak_date: Decimal("83.5"),
            closing_date: Decimal("83.5"),
        }
    )
    stock_provider = _FakeStockPriceProvider(
        peak=(peak_date, Decimal("50")), closing=(closing_date, Decimal("48"))
    )
    return A3Service(
        engine=ItrCalculationEngine(),
        a3_repository=None,  # type: ignore[arg-type]  # unused when session_id is None
        session_repository=None,  # type: ignore[arg-type]
        market_data_provider=fx_provider,  # type: ignore[arg-type]
        stock_price_provider=stock_provider,  # type: ignore[arg-type]
    )


class TestCalculateFromLots:
    async def test_aggregates_lots_by_acquisition_date(self, service: A3Service):
        holding = A3HoldingRequest(
            country="UNITED_STATES_OF_AMERICA",
            entity_name="Cisco Systems Inc",
            entity_address="170 West Tasman Drive San Jose CA 95134",
            zip_code="95134",
            ticker="CSCO",
            currency="USD",
            lots=[
                A3LotRequest(date_acquired=date(2023, 6, 30), cost=Decimal("2121.34"), quantity=Decimal("41")),
                A3LotRequest(date_acquired=date(2023, 6, 30), cost=Decimal("100"), quantity=Decimal("2")),
            ],
        )
        response = await service.calculate_from_lots(
            A3CalculateFromLotsRequest(session_id=None, holding=holding)
        )

        assert response.summary.row_count == 1
        row = response.rows[0]
        assert row.acquisition_date == date(2023, 6, 30)
        # initial = (2121.34 + 100) * 82 = 182149.88 -> rounds to 182150
        assert row.initial_investment == Decimal("182150")
        # peak = 43 qty * 50 * 83.5 = 179525
        assert row.peak_investment == Decimal("179525")
        # closing = 43 qty * 48 * 83.5 = 172344
        assert row.closing_balance == Decimal("172344")
        assert row.total_gross_amount == row.initial_investment
        assert row.sales_proceeds == Decimal("0")

    async def test_separate_dates_produce_separate_rows(self, service: A3Service):
        holding = A3HoldingRequest(
            country="UNITED_STATES_OF_AMERICA",
            entity_name="Cisco Systems Inc",
            entity_address="170 West Tasman Drive San Jose CA 95134",
            zip_code="95134",
            ticker="CSCO",
            currency="USD",
            lots=[
                A3LotRequest(date_acquired=date(2023, 6, 30), cost=Decimal("2121.34"), quantity=Decimal("41")),
                A3LotRequest(date_acquired=date(2023, 12, 29), cost=Decimal("2323.92"), quantity=Decimal("46")),
            ],
        )
        # Second lot's date needs its own fx rate; extend the fake provider's map.
        service._market_data_provider._rates[date(2023, 12, 29)] = Decimal("83.5")  # noqa: SLF001

        response = await service.calculate_from_lots(
            A3CalculateFromLotsRequest(session_id=None, holding=holding)
        )

        assert response.summary.row_count == 2
        dates = {row.acquisition_date for row in response.rows}
        assert dates == {date(2023, 6, 30), date(2023, 12, 29)}
