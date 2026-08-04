"""Concrete SQLAlchemy 2.x repository implementations."""
from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.a3 import ForeignTaxCreditDetail
from app.domain.entities.fsi import ForeignSourceIncome
from app.persistence.models import A3Entry, FsiEntry, TaxSession


class SqlAlchemySessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, name: str, assessment_year: str, owner_ref: str | None) -> str:
        session = TaxSession(name=name, assessment_year=assessment_year, owner_ref=owner_ref)
        self._db.add(session)
        await self._db.flush()
        await self._db.commit()
        return session.id

    async def get(self, session_id: str) -> dict | None:
        result = await self._db.get(TaxSession, session_id)
        if result is None:
            return None
        return {
            "id": result.id,
            "name": result.name,
            "assessment_year": result.assessment_year,
            "owner_ref": result.owner_ref,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
        }

    async def list(self, skip: int, limit: int) -> tuple[list[dict], int]:
        total = (await self._db.execute(select(func.count(TaxSession.id)))).scalar_one()
        rows = (
            await self._db.execute(
                select(TaxSession).order_by(TaxSession.updated_at.desc()).offset(skip).limit(limit)
            )
        ).scalars().all()
        items = [
            {
                "id": r.id,
                "name": r.name,
                "assessment_year": r.assessment_year,
                "owner_ref": r.owner_ref,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in rows
        ]
        return items, total

    async def touch(self, session_id: str) -> None:
        from datetime import datetime

        session = await self._db.get(TaxSession, session_id)
        if session is not None:
            session.updated_at = datetime.utcnow()
            await self._db.commit()

    async def update_metadata(self, session_id: str, name: str, assessment_year: str) -> None:
        from datetime import datetime

        session = await self._db.get(TaxSession, session_id)
        if session is not None:
            session.name = name
            session.assessment_year = assessment_year
            session.updated_at = datetime.utcnow()
            await self._db.commit()

    async def delete(self, session_id: str) -> None:
        await self._db.execute(delete(TaxSession).where(TaxSession.id == session_id))
        await self._db.commit()

    async def exists(self, session_id: str) -> bool:
        result = await self._db.get(TaxSession, session_id)
        return result is not None


class SqlAlchemyFsiRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def add_many(self, session_id: str, entries: list[ForeignSourceIncome]) -> None:
        self._db.add_all(
            [
                FsiEntry(
                    session_id=session_id,
                    country=e.country,
                    income_source=e.income_source,
                    income_amount=e.income_amount,
                    tax_paid_outside_india=e.tax_paid_outside_india,
                    tax_payable_in_india=e.tax_payable_in_india,
                    dtaa_rate=e.dtaa_rate,
                    currency=e.currency,
                    exchange_rate=e.exchange_rate,
                    assessment_year=e.assessment_year,
                )
                for e in entries
            ]
        )
        await self._db.commit()

    async def replace_all(self, session_id: str, entries: list[ForeignSourceIncome]) -> None:
        await self._db.execute(delete(FsiEntry).where(FsiEntry.session_id == session_id))
        await self.add_many(session_id, entries)

    async def list(
        self, session_id: str, skip: int, limit: int
    ) -> tuple[list[ForeignSourceIncome], int]:
        total = (
            await self._db.execute(
                select(func.count(FsiEntry.id)).where(FsiEntry.session_id == session_id)
            )
        ).scalar_one()
        rows = (
            await self._db.execute(
                select(FsiEntry)
                .where(FsiEntry.session_id == session_id)
                .order_by(FsiEntry.created_at)
                .offset(skip)
                .limit(limit)
            )
        ).scalars().all()
        items = [
            ForeignSourceIncome(
                country=r.country,
                income_source=r.income_source,
                income_amount=r.income_amount,
                tax_paid_outside_india=r.tax_paid_outside_india,
                tax_payable_in_india=r.tax_payable_in_india,
                dtaa_rate=r.dtaa_rate,
                currency=r.currency,
                exchange_rate=r.exchange_rate,
                assessment_year=r.assessment_year,
            )
            for r in rows
        ]
        return items, total


class SqlAlchemyA3Repository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def add_many(self, session_id: str, entries: list[ForeignTaxCreditDetail]) -> None:
        self._db.add_all(
            [
                A3Entry(
                    session_id=session_id,
                    country=e.country,
                    entity_name=e.entity_name,
                    entity_address=e.entity_address,
                    zip_code=e.zip_code,
                    nature_of_entity=e.nature_of_entity,
                    acquisition_date=e.acquisition_date,
                    currency=e.currency,
                    initial_investment_foreign=e.initial_investment_foreign,
                    peak_investment_foreign=e.peak_investment_foreign,
                    closing_balance_foreign=e.closing_balance_foreign,
                    sales_proceeds_foreign=e.sales_proceeds_foreign,
                    acquisition_exchange_rate=e.acquisition_exchange_rate,
                    peak_exchange_rate=e.peak_exchange_rate,
                    closing_exchange_rate=e.closing_exchange_rate,
                    dtaa_article=e.dtaa_article,
                    foreign_tax_paid=e.foreign_tax_paid,
                    foreign_tax_credit_claimed=e.foreign_tax_credit_claimed,
                )
                for e in entries
            ]
        )
        await self._db.commit()

    async def replace_all(self, session_id: str, entries: list[ForeignTaxCreditDetail]) -> None:
        await self._db.execute(delete(A3Entry).where(A3Entry.session_id == session_id))
        await self.add_many(session_id, entries)

    async def list(
        self, session_id: str, skip: int, limit: int
    ) -> tuple[list[ForeignTaxCreditDetail], int]:
        total = (
            await self._db.execute(
                select(func.count(A3Entry.id)).where(A3Entry.session_id == session_id)
            )
        ).scalar_one()
        rows = (
            await self._db.execute(
                select(A3Entry)
                .where(A3Entry.session_id == session_id)
                .order_by(A3Entry.created_at)
                .offset(skip)
                .limit(limit)
            )
        ).scalars().all()
        items = [
            ForeignTaxCreditDetail(
                country=r.country,
                entity_name=r.entity_name,
                entity_address=r.entity_address,
                zip_code=r.zip_code,
                nature_of_entity=r.nature_of_entity,
                acquisition_date=r.acquisition_date,
                currency=r.currency,
                initial_investment_foreign=r.initial_investment_foreign,
                peak_investment_foreign=r.peak_investment_foreign,
                closing_balance_foreign=r.closing_balance_foreign,
                sales_proceeds_foreign=r.sales_proceeds_foreign,
                acquisition_exchange_rate=r.acquisition_exchange_rate,
                peak_exchange_rate=r.peak_exchange_rate,
                closing_exchange_rate=r.closing_exchange_rate,
                dtaa_article=r.dtaa_article,
                foreign_tax_paid=r.foreign_tax_paid,
                foreign_tax_credit_claimed=r.foreign_tax_credit_claimed,
            )
            for r in rows
        ]
        return items, total
