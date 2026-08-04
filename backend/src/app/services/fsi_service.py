"""Service layer for Schedule FSI: orchestrates validation, engine, and persistence.

Business/orchestration logic lives here, never in the API controllers.
"""
from dataclasses import asdict

from app.core.exceptions import NotFoundError
from app.domain.engine.interface import TaxCalculationEngine
from app.domain.entities.fsi import ForeignSourceIncome
from app.dto.fsi import (
    FsiCalculateRequest,
    FsiCalculateResponse,
    FsiEntryRequest,
    FsiListResponse,
    FsiResultRowResponse,
    FsiSummaryResponse,
)
from app.repositories.interfaces import FsiRepository, SessionRepository


def fsi_entry_to_domain(entry: FsiEntryRequest) -> ForeignSourceIncome:
    return ForeignSourceIncome(**entry.model_dump())


class FsiService:
    def __init__(
        self,
        engine: TaxCalculationEngine,
        fsi_repository: FsiRepository,
        session_repository: SessionRepository,
    ) -> None:
        self._engine = engine
        self._fsi_repository = fsi_repository
        self._session_repository = session_repository

    async def calculate(self, request: FsiCalculateRequest) -> FsiCalculateResponse:
        entities = [fsi_entry_to_domain(e) for e in request.entries]
        rows, summary = self._engine.generate_fsi(entities)

        if request.session_id is not None:
            if not await self._session_repository.exists(request.session_id):
                raise NotFoundError(f"Session '{request.session_id}' not found")
            await self._fsi_repository.replace_all(request.session_id, entities)
            await self._session_repository.touch(request.session_id)

        return FsiCalculateResponse(
            session_id=request.session_id,
            rows=[FsiResultRowResponse(**asdict(r)) for r in rows],
            summary=FsiSummaryResponse(**asdict(summary)),
        )

    async def list_entries(self, session_id: str, skip: int, limit: int) -> FsiListResponse:
        items, total = await self._fsi_repository.list(session_id, skip, limit)
        return FsiListResponse(
            items=[FsiEntryRequest(**asdict(i)) for i in items], total=total, skip=skip, limit=limit
        )
