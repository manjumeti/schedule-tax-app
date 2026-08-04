"""Domain entities for Schedule FSI (Foreign Source Income).

Domain entities are plain, framework-agnostic dataclasses: no Pydantic/SQLAlchemy
imports here, so business rules stay independent of transport or persistence concerns.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ForeignSourceIncome:
    """A single Schedule FSI input row (one country/income-source combination)."""

    country: str
    income_source: str
    income_amount: Decimal
    tax_paid_outside_india: Decimal
    tax_payable_in_india: Decimal
    dtaa_rate: Decimal  # percentage, e.g. 10 for 10%
    currency: str
    exchange_rate: Decimal
    assessment_year: str


@dataclass(frozen=True, slots=True)
class FsiResultRow:
    """A calculated Schedule FSI output row, in INR."""

    country: str
    income_source: str
    income: Decimal
    tax_paid: Decimal
    dtaa_rate: Decimal
    relief_claimed: Decimal
    net_tax: Decimal
    assessment_year: str


@dataclass(frozen=True, slots=True)
class FsiSummary:
    total_income: Decimal
    total_tax_paid: Decimal
    total_relief_claimed: Decimal
    total_net_tax: Decimal
    row_count: int
