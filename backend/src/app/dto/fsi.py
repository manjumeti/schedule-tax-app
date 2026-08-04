"""Request/response DTOs for Schedule FSI (Pydantic v2)."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.dto.common import (
    validate_assessment_year,
    validate_country,
    validate_currency,
    validate_percentage,
    validate_positive,
)


class FsiEntryRequest(BaseModel):
    """A single Schedule FSI input row submitted by the user."""

    model_config = ConfigDict(str_strip_whitespace=True)

    country: str = Field(..., min_length=2, max_length=100)
    income_source: str = Field(..., min_length=2, max_length=200)
    income_amount: Decimal = Field(..., gt=0, description="Foreign income amount, in `currency`")
    tax_paid_outside_india: Decimal = Field(..., ge=0)
    tax_payable_in_india: Decimal = Field(..., ge=0)
    dtaa_rate: Decimal = Field(..., ge=0, le=100, description="DTAA relief rate, percent")
    currency: str = Field(..., min_length=3, max_length=3)
    exchange_rate: Decimal = Field(..., gt=0)
    assessment_year: str = Field(..., examples=["2025-26"])

    @field_validator("country")
    @classmethod
    def _country(cls, v: str) -> str:
        return validate_country(v)

    @field_validator("currency")
    @classmethod
    def _currency(cls, v: str) -> str:
        return validate_currency(v)

    @field_validator("assessment_year")
    @classmethod
    def _assessment_year(cls, v: str) -> str:
        return validate_assessment_year(v)

    @field_validator("dtaa_rate")
    @classmethod
    def _dtaa_rate(cls, v: Decimal) -> Decimal:
        return validate_percentage(v, "dtaa_rate")

    @field_validator("tax_paid_outside_india", "tax_payable_in_india")
    @classmethod
    def _non_negative(cls, v: Decimal) -> Decimal:
        return validate_positive(v)

    @model_validator(mode="after")
    def _cross_field_checks(self) -> "FsiEntryRequest":
        if self.tax_paid_outside_india > self.income_amount * 2:
            raise ValueError(
                "tax_paid_outside_india looks implausible relative to income_amount "
                "(more than 2x income); please verify."
            )
        return self


class FsiCalculateRequest(BaseModel):
    session_id: str | None = Field(default=None, description="Attach results to an existing session")
    entries: list[FsiEntryRequest] = Field(..., min_length=1, max_length=10_000)


class FsiResultRowResponse(BaseModel):
    country: str
    income_source: str
    income: Decimal
    tax_paid: Decimal
    dtaa_rate: Decimal
    relief_claimed: Decimal
    net_tax: Decimal
    assessment_year: str


class FsiSummaryResponse(BaseModel):
    total_income: Decimal
    total_tax_paid: Decimal
    total_relief_claimed: Decimal
    total_net_tax: Decimal
    row_count: int


class FsiCalculateResponse(BaseModel):
    session_id: str | None
    rows: list[FsiResultRowResponse]
    summary: FsiSummaryResponse


class FsiListResponse(BaseModel):
    items: list[FsiEntryRequest]
    total: int
    skip: int
    limit: int
