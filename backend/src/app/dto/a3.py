"""Request/response DTOs for Form A3 (Pydantic v2)."""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.dto.common import validate_country, validate_currency


class A3EntryRequest(BaseModel):
    """A single Form A3 input row: foreign tax credit / DTAA support detail."""

    model_config = ConfigDict(str_strip_whitespace=True)

    country: str = Field(..., min_length=2, max_length=100)
    entity_name: str = Field(..., min_length=2, max_length=200)
    entity_address: str = Field(..., min_length=2, max_length=500)
    zip_code: str = Field(..., min_length=2, max_length=20)
    nature_of_entity: str = Field(..., min_length=2, max_length=100)
    acquisition_date: date
    currency: str = Field(..., min_length=3, max_length=3)
    initial_investment_foreign: Decimal = Field(..., ge=0)
    peak_investment_foreign: Decimal = Field(..., ge=0)
    closing_balance_foreign: Decimal = Field(..., ge=0)
    sales_proceeds_foreign: Decimal = Field(default=Decimal(0), ge=0)
    acquisition_exchange_rate: Decimal = Field(..., gt=0)
    peak_exchange_rate: Decimal = Field(..., gt=0)
    closing_exchange_rate: Decimal = Field(..., gt=0)
    dtaa_article: str = Field(..., min_length=1, max_length=100)
    foreign_tax_paid: Decimal = Field(default=Decimal(0), ge=0)
    foreign_tax_credit_claimed: Decimal = Field(default=Decimal(0), ge=0)

    @field_validator("country")
    @classmethod
    def _country(cls, v: str) -> str:
        return validate_country(v)

    @field_validator("currency")
    @classmethod
    def _currency(cls, v: str) -> str:
        return validate_currency(v)

    @field_validator("acquisition_date")
    @classmethod
    def _acquisition_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("acquisition_date cannot be in the future.")
        return v

    @model_validator(mode="after")
    def _cross_field_checks(self) -> "A3EntryRequest":
        if self.foreign_tax_credit_claimed > self.foreign_tax_paid:
            raise ValueError("foreign_tax_credit_claimed cannot exceed foreign_tax_paid.")
        return self


class A3CalculateRequest(BaseModel):
    session_id: str | None = None
    entries: list[A3EntryRequest] = Field(..., min_length=1, max_length=10_000)


class A3LotRequest(BaseModel):
    """A single RSU/ESPP vest lot: what the user actually receives from a broker statement."""

    model_config = ConfigDict(str_strip_whitespace=True)

    date_acquired: date
    cost: Decimal = Field(..., gt=0, description="Total cost/FMV of the lot in the holding's currency.")
    quantity: Decimal = Field(..., gt=0)

    @field_validator("date_acquired")
    @classmethod
    def _not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("date_acquired cannot be in the future.")
        return v


class A3HoldingRequest(BaseModel):
    """Entity/ticker metadata entered once per holding; lots are aggregated by acquisition date."""

    model_config = ConfigDict(str_strip_whitespace=True)

    country: str = Field(..., min_length=2, max_length=100)
    entity_name: str = Field(..., min_length=2, max_length=200)
    entity_address: str = Field(..., min_length=2, max_length=500)
    zip_code: str = Field(..., min_length=2, max_length=20)
    nature_of_entity: str = Field(default="Company", min_length=2, max_length=100)
    ticker: str = Field(..., min_length=1, max_length=15)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    lots: list[A3LotRequest] = Field(..., min_length=1, max_length=1000)

    @field_validator("country")
    @classmethod
    def _country(cls, v: str) -> str:
        return validate_country(v)

    @field_validator("currency")
    @classmethod
    def _currency(cls, v: str) -> str:
        return validate_currency(v)

    @field_validator("ticker")
    @classmethod
    def _ticker(cls, v: str) -> str:
        return v.upper()


class A3CalculateFromLotsRequest(BaseModel):
    session_id: str | None = None
    holding: A3HoldingRequest


class A3ResultRowResponse(BaseModel):
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


class A3SummaryResponse(BaseModel):
    total_initial_investment: Decimal
    total_peak_investment: Decimal
    total_closing_balance: Decimal
    total_foreign_tax_credit_claimed: Decimal
    row_count: int


class A3CalculateResponse(BaseModel):
    session_id: str | None
    rows: list[A3ResultRowResponse]
    summary: A3SummaryResponse


class A3ListResponse(BaseModel):
    items: list[A3EntryRequest]
    total: int
    skip: int
    limit: int
