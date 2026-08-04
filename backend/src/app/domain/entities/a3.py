"""Domain entities for Form A3 (foreign tax credit / DTAA relief support schedule).

Mirrors the field set produced by the existing `itr` repository's
`generate_schedule_fa_a3.py` script (Country, Name/Address of Entity, Date of
Acquisition, Initial/Peak/Closing values, Total Gross Amount, Sales proceeds),
extended with the DTAA/foreign-tax-credit fields required by Form A3.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ForeignTaxCreditDetail:
    """A single Form A3 input row."""

    country: str
    entity_name: str
    entity_address: str
    zip_code: str
    nature_of_entity: str
    acquisition_date: date
    currency: str
    initial_investment_foreign: Decimal
    peak_investment_foreign: Decimal
    closing_balance_foreign: Decimal
    sales_proceeds_foreign: Decimal
    acquisition_exchange_rate: Decimal
    peak_exchange_rate: Decimal
    closing_exchange_rate: Decimal
    dtaa_article: str
    foreign_tax_paid: Decimal
    foreign_tax_credit_claimed: Decimal


@dataclass(frozen=True, slots=True)
class A3ResultRow:
    """A calculated Form A3 output row, values converted to INR."""

    country: str
    entity_name: str
    entity_address: str
    zip_code: str
    nature_of_entity: str
    acquisition_date: date
    initial_investment: Decimal | None
    peak_investment: Decimal | None
    closing_balance: Decimal | None
    total_gross_amount: Decimal | None
    sales_proceeds: Decimal
    dtaa_article: str
    foreign_tax_credit_claimed: Decimal


@dataclass(frozen=True, slots=True)
class A3Summary:
    total_initial_investment: Decimal
    total_peak_investment: Decimal
    total_closing_balance: Decimal
    total_foreign_tax_credit_claimed: Decimal
    row_count: int
