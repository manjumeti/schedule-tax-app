"""SQLAlchemy 2.x ORM models (persistence layer).

Normalized per-row tables (rather than JSON blobs) so that entry lists can be
paginated and filtered efficiently at the database level for large datasets.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class TaxSession(Base):
    """A saved user workspace: one assessment year's worth of FSI/A3 data."""

    __tablename__ = "tax_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200))
    assessment_year: Mapped[str] = mapped_column(String(9))
    owner_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    fsi_entries: Mapped[list["FsiEntry"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    a3_entries: Mapped[list["A3Entry"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class FsiEntry(Base):
    __tablename__ = "fsi_entries"
    __table_args__ = (Index("ix_fsi_entries_session_id", "session_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("tax_sessions.id", ondelete="CASCADE"))
    country: Mapped[str] = mapped_column(String(100))
    income_source: Mapped[str] = mapped_column(String(200))
    income_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    tax_paid_outside_india: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    tax_payable_in_india: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    dtaa_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    currency: Mapped[str] = mapped_column(String(3))
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    assessment_year: Mapped[str] = mapped_column(String(9))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    session: Mapped["TaxSession"] = relationship(back_populates="fsi_entries")


class A3Entry(Base):
    __tablename__ = "a3_entries"
    __table_args__ = (Index("ix_a3_entries_session_id", "session_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("tax_sessions.id", ondelete="CASCADE"))
    country: Mapped[str] = mapped_column(String(100))
    entity_name: Mapped[str] = mapped_column(String(200))
    entity_address: Mapped[str] = mapped_column(Text)
    zip_code: Mapped[str] = mapped_column(String(20))
    nature_of_entity: Mapped[str] = mapped_column(String(100))
    acquisition_date: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3))
    initial_investment_foreign: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    peak_investment_foreign: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    closing_balance_foreign: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    sales_proceeds_foreign: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    acquisition_exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    peak_exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    closing_exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    dtaa_article: Mapped[str] = mapped_column(String(100))
    foreign_tax_paid: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    foreign_tax_credit_claimed: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    session: Mapped["TaxSession"] = relationship(back_populates="a3_entries")
