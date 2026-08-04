"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-31

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tax_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("assessment_year", sa.String(length=9), nullable=False),
        sa.Column("owner_ref", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "fsi_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(length=36),
            sa.ForeignKey("tax_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("income_source", sa.String(length=200), nullable=False),
        sa.Column("income_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("tax_paid_outside_india", sa.Numeric(18, 2), nullable=False),
        sa.Column("tax_payable_in_india", sa.Numeric(18, 2), nullable=False),
        sa.Column("dtaa_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("exchange_rate", sa.Numeric(12, 4), nullable=False),
        sa.Column("assessment_year", sa.String(length=9), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fsi_entries_session_id", "fsi_entries", ["session_id"])

    op.create_table(
        "a3_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(length=36),
            sa.ForeignKey("tax_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("entity_name", sa.String(length=200), nullable=False),
        sa.Column("entity_address", sa.Text(), nullable=False),
        sa.Column("zip_code", sa.String(length=20), nullable=False),
        sa.Column("nature_of_entity", sa.String(length=100), nullable=False),
        sa.Column("acquisition_date", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("initial_investment_foreign", sa.Numeric(18, 2), nullable=False),
        sa.Column("peak_investment_foreign", sa.Numeric(18, 2), nullable=False),
        sa.Column("closing_balance_foreign", sa.Numeric(18, 2), nullable=False),
        sa.Column("sales_proceeds_foreign", sa.Numeric(18, 2), nullable=False),
        sa.Column("acquisition_exchange_rate", sa.Numeric(12, 4), nullable=False),
        sa.Column("peak_exchange_rate", sa.Numeric(12, 4), nullable=False),
        sa.Column("closing_exchange_rate", sa.Numeric(12, 4), nullable=False),
        sa.Column("dtaa_article", sa.String(length=100), nullable=False),
        sa.Column("foreign_tax_paid", sa.Numeric(18, 2), nullable=False),
        sa.Column("foreign_tax_credit_claimed", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_a3_entries_session_id", "a3_entries", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_a3_entries_session_id", table_name="a3_entries")
    op.drop_table("a3_entries")
    op.drop_index("ix_fsi_entries_session_id", table_name="fsi_entries")
    op.drop_table("fsi_entries")
    op.drop_table("tax_sessions")
