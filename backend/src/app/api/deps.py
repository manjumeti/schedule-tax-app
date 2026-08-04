"""FastAPI dependency-injection wiring.

Centralizing DI here means endpoints only ever depend on service classes,
never on repositories or the engine directly, and it makes it trivial to
override dependencies in tests (`app.dependency_overrides[...]`).
"""
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain.engine.interface import TaxCalculationEngine
from app.domain.engine.itr_engine import ItrCalculationEngine
from app.domain.engine.market_data import (
    MarketDataProvider,
    StockPriceProvider,
    build_market_data_provider,
    build_stock_price_provider,
)
from app.persistence.database import get_db_session
from app.repositories.sqlalchemy_repositories import (
    SqlAlchemyA3Repository,
    SqlAlchemyFsiRepository,
    SqlAlchemySessionRepository,
)
from app.services.a3_service import A3Service
from app.services.dashboard_service import DashboardService
from app.services.export_service import ExportService
from app.services.fsi_service import FsiService
from app.services.session_service import SessionService

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@lru_cache
def get_engine() -> TaxCalculationEngine:
    return ItrCalculationEngine()


@lru_cache
def get_market_data_provider() -> MarketDataProvider:
    settings = get_settings()
    return build_market_data_provider(settings.market_data_provider, settings.sbi_rates_csv_dir)


@lru_cache
def get_stock_price_provider() -> StockPriceProvider:
    settings = get_settings()
    return build_stock_price_provider(settings.market_data_provider)


def get_fsi_service(db: DbSession) -> FsiService:
    return FsiService(get_engine(), SqlAlchemyFsiRepository(db), SqlAlchemySessionRepository(db))


def get_a3_service(db: DbSession) -> A3Service:
    return A3Service(
        get_engine(),
        SqlAlchemyA3Repository(db),
        SqlAlchemySessionRepository(db),
        get_market_data_provider(),
        get_stock_price_provider(),
    )


def get_session_service(db: DbSession) -> SessionService:
    return SessionService(
        SqlAlchemySessionRepository(db),
        SqlAlchemyFsiRepository(db),
        SqlAlchemyA3Repository(db),
    )


def get_dashboard_service(db: DbSession) -> DashboardService:
    return DashboardService(
        SqlAlchemySessionRepository(db),
        SqlAlchemyFsiRepository(db),
        SqlAlchemyA3Repository(db),
    )


def get_export_service(db: DbSession) -> ExportService:
    return ExportService(
        get_engine(),
        SqlAlchemySessionRepository(db),
        SqlAlchemyFsiRepository(db),
        SqlAlchemyA3Repository(db),
    )
