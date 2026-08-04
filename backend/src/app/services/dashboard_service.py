"""Service layer for the dashboard summary view."""
from decimal import Decimal

from app.core.exceptions import NotFoundError
from app.dto.dashboard import DashboardResponse, ValidationStatus
from app.repositories.interfaces import A3Repository, FsiRepository, SessionRepository

_ZERO = Decimal("0")
_LARGE_LIMIT = 50_000


class DashboardService:
    def __init__(
        self,
        session_repository: SessionRepository,
        fsi_repository: FsiRepository,
        a3_repository: A3Repository,
    ) -> None:
        self._session_repository = session_repository
        self._fsi_repository = fsi_repository
        self._a3_repository = a3_repository

    async def get_dashboard(self, session_id: str) -> DashboardResponse:
        if not await self._session_repository.exists(session_id):
            raise NotFoundError(f"Session '{session_id}' not found")

        fsi_items, _ = await self._fsi_repository.list(session_id, 0, _LARGE_LIMIT)
        a3_items, a3_total = await self._a3_repository.list(session_id, 0, _LARGE_LIMIT)

        total_dividend_income = sum(
            (e.income_amount * e.exchange_rate for e in fsi_items if "dividend" in e.income_source.lower()),
            _ZERO,
        )
        total_tax_paid_outside_india = sum(
            (e.tax_paid_outside_india * e.exchange_rate for e in fsi_items), _ZERO
        )

        generated_schedules = []
        if fsi_items:
            generated_schedules.append("Schedule FSI")
        if a3_items:
            generated_schedules.append("Form A3")

        error_count = 0
        warning_count = 0
        if not fsi_items and not a3_items:
            warning_count += 1  # nothing entered yet

        return DashboardResponse(
            session_id=session_id,
            total_foreign_accounts=a3_total,
            total_dividend_income=total_dividend_income,
            total_tax_paid_outside_india=total_tax_paid_outside_india,
            generated_schedules=generated_schedules,
            validation_status=ValidationStatus(
                is_valid=error_count == 0, error_count=error_count, warning_count=warning_count
            ),
        )
