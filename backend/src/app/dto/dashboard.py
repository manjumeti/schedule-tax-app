"""Request/response DTOs for the dashboard summary."""
from decimal import Decimal

from pydantic import BaseModel


class ValidationStatus(BaseModel):
    is_valid: bool
    error_count: int
    warning_count: int


class DashboardResponse(BaseModel):
    session_id: str
    total_foreign_accounts: int
    total_dividend_income: Decimal
    total_tax_paid_outside_india: Decimal
    generated_schedules: list[str]
    validation_status: ValidationStatus
