"""Integration tests for SQLAlchemy repositories against a real (in-memory) DB."""
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.fsi import ForeignSourceIncome
from app.repositories.sqlalchemy_repositories import (
    SqlAlchemyFsiRepository,
    SqlAlchemySessionRepository,
)

pytestmark = pytest.mark.asyncio


async def test_session_repository_crud(db_session: AsyncSession):
    repo = SqlAlchemySessionRepository(db_session)
    session_id = await repo.create("My Filing", "2025-26", owner_ref=None)

    assert await repo.exists(session_id) is True
    fetched = await repo.get(session_id)
    assert fetched["name"] == "My Filing"

    items, total = await repo.list(0, 10)
    assert total == 1
    assert items[0]["id"] == session_id

    await repo.delete(session_id)
    assert await repo.exists(session_id) is False


async def test_fsi_repository_pagination(db_session: AsyncSession):
    session_repo = SqlAlchemySessionRepository(db_session)
    session_id = await session_repo.create("Filing", "2025-26", None)

    fsi_repo = SqlAlchemyFsiRepository(db_session)
    entries = [
        ForeignSourceIncome(
            country="UNITED_STATES_OF_AMERICA",
            income_source=f"Dividend {i}",
            income_amount=Decimal("100"),
            tax_paid_outside_india=Decimal("10"),
            tax_payable_in_india=Decimal("20"),
            dtaa_rate=Decimal("10"),
            currency="USD",
            exchange_rate=Decimal("83"),
            assessment_year="2025-26",
        )
        for i in range(5)
    ]
    await fsi_repo.add_many(session_id, entries)

    page1, total = await fsi_repo.list(session_id, skip=0, limit=2)
    assert total == 5
    assert len(page1) == 2

    page2, _ = await fsi_repo.list(session_id, skip=2, limit=2)
    assert len(page2) == 2
