"""Service layer for Form A3."""
from collections import defaultdict
from dataclasses import asdict
from decimal import Decimal

from app.core.exceptions import NotFoundError
from app.domain.engine.interface import TaxCalculationEngine
from app.domain.engine.market_data import MarketDataProvider, StockPriceProvider
from app.domain.entities.a3 import ForeignTaxCreditDetail
from app.dto.a3 import (
    A3CalculateFromLotsRequest,
    A3CalculateRequest,
    A3CalculateResponse,
    A3EntryRequest,
    A3ListResponse,
    A3ResultRowResponse,
    A3SummaryResponse,
)
from app.repositories.interfaces import A3Repository, SessionRepository


def a3_entry_to_domain(entry: A3EntryRequest) -> ForeignTaxCreditDetail:
    return ForeignTaxCreditDetail(**entry.model_dump())


class A3Service:
    def __init__(
        self,
        engine: TaxCalculationEngine,
        a3_repository: A3Repository,
        session_repository: SessionRepository,
        market_data_provider: MarketDataProvider | None = None,
        stock_price_provider: StockPriceProvider | None = None,
    ) -> None:
        self._engine = engine
        self._a3_repository = a3_repository
        self._session_repository = session_repository
        self._market_data_provider = market_data_provider
        self._stock_price_provider = stock_price_provider

    async def calculate(self, request: A3CalculateRequest) -> A3CalculateResponse:
        entities = [a3_entry_to_domain(e) for e in request.entries]
        return await self._calculate_and_persist(entities, request.session_id)

    async def calculate_from_lots(self, request: A3CalculateFromLotsRequest) -> A3CalculateResponse:
        """Aggregate RSU/ESPP vest lots by acquisition date and auto-fetch FX/stock prices.

        Mirrors `generate_schedule_fa_a3.py` in the `itr` repository: one input row per
        vest lot (date, cost, quantity) becomes one Form A3 row per unique acquisition date.
        """
        if self._market_data_provider is None or self._stock_price_provider is None:
            raise NotFoundError(
                "Automatic lot-based calculation requires a configured market data provider."
            )

        holding = request.holding
        aggregated: dict[object, tuple[Decimal, Decimal]] = defaultdict(
            lambda: (Decimal(0), Decimal(0))
        )
        for lot in holding.lots:
            total_cost, total_qty = aggregated[lot.date_acquired]
            aggregated[lot.date_acquired] = (total_cost + lot.cost, total_qty + lot.quantity)

        entities: list[ForeignTaxCreditDetail] = []
        for acquisition_date in sorted(aggregated.keys()):
            total_cost, total_qty = aggregated[acquisition_date]
            acquisition_rate = self._market_data_provider.get_fx_rate(
                holding.currency, acquisition_date
            )
            peak_date, peak_price, closing_date, closing_price = (
                self._stock_price_provider.get_peak_and_closing(
                    holding.ticker, acquisition_date.year
                )
            )
            peak_rate = self._market_data_provider.get_fx_rate(holding.currency, peak_date)
            closing_rate = self._market_data_provider.get_fx_rate(holding.currency, closing_date)

            entities.append(
                ForeignTaxCreditDetail(
                    country=holding.country,
                    entity_name=holding.entity_name,
                    entity_address=holding.entity_address,
                    zip_code=holding.zip_code,
                    nature_of_entity=holding.nature_of_entity,
                    acquisition_date=acquisition_date,
                    currency=holding.currency,
                    initial_investment_foreign=total_cost,
                    peak_investment_foreign=total_qty * peak_price,
                    closing_balance_foreign=total_qty * closing_price,
                    sales_proceeds_foreign=Decimal(0),
                    acquisition_exchange_rate=acquisition_rate,
                    peak_exchange_rate=peak_rate,
                    closing_exchange_rate=closing_rate,
                    dtaa_article="N/A",
                    foreign_tax_paid=Decimal(0),
                    foreign_tax_credit_claimed=Decimal(0),
                )
            )

        return await self._calculate_and_persist(entities, request.session_id)

    async def _calculate_and_persist(
        self, entities: list[ForeignTaxCreditDetail], session_id: str | None
    ) -> A3CalculateResponse:
        rows, summary = self._engine.generate_a3(entities)

        if session_id is not None:
            if not await self._session_repository.exists(session_id):
                raise NotFoundError(f"Session '{session_id}' not found")
            await self._a3_repository.replace_all(session_id, entities)
            await self._session_repository.touch(session_id)

        return A3CalculateResponse(
            session_id=session_id,
            rows=[A3ResultRowResponse(**asdict(r)) for r in rows],
            summary=A3SummaryResponse(**asdict(summary)),
        )

    async def list_entries(self, session_id: str, skip: int, limit: int) -> A3ListResponse:
        items, total = await self._a3_repository.list(session_id, skip, limit)
        return A3ListResponse(
            items=[A3EntryRequest(**asdict(i)) for i in items], total=total, skip=skip, limit=limit
        )

