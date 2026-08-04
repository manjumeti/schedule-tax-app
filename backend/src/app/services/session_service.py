"""Service layer for session save/reload."""
from __future__ import annotations

from dataclasses import asdict

from app.core.exceptions import NotFoundError
from app.dto.a3 import A3EntryRequest
from app.dto.fsi import FsiEntryRequest
from app.dto.session import (
    SessionDetailResponse,
    SessionListResponse,
    SessionSaveRequest,
    SessionSummaryResponse,
)
from app.repositories.interfaces import A3Repository, FsiRepository, SessionRepository
from app.services.a3_service import a3_entry_to_domain
from app.services.fsi_service import fsi_entry_to_domain

_MAX_RELOAD_ROWS = 50_000


class SessionService:
    def __init__(
        self,
        session_repository: SessionRepository,
        fsi_repository: FsiRepository,
        a3_repository: A3Repository,
    ) -> None:
        self._session_repository = session_repository
        self._fsi_repository = fsi_repository
        self._a3_repository = a3_repository

    async def save(self, request: SessionSaveRequest) -> SessionDetailResponse:
        if request.session_id is not None:
            if not await self._session_repository.exists(request.session_id):
                raise NotFoundError(f"Session '{request.session_id}' not found")
            session_id = request.session_id
            await self._session_repository.update_metadata(
                session_id, request.name, request.assessment_year
            )
        else:
            session_id = await self._session_repository.create(
                request.name, request.assessment_year, request.owner_ref
            )

        await self._fsi_repository.replace_all(
            session_id, [fsi_entry_to_domain(e) for e in request.fsi_entries]
        )
        await self._a3_repository.replace_all(
            session_id, [a3_entry_to_domain(e) for e in request.a3_entries]
        )

        return await self.get(session_id)

    async def get(self, session_id: str) -> SessionDetailResponse:
        session = await self._session_repository.get(session_id)
        if session is None:
            raise NotFoundError(f"Session '{session_id}' not found")

        fsi_items, _ = await self._fsi_repository.list(session_id, 0, _MAX_RELOAD_ROWS)
        a3_items, _ = await self._a3_repository.list(session_id, 0, _MAX_RELOAD_ROWS)

        return SessionDetailResponse(
            id=session["id"],
            name=session["name"],
            assessment_year=session["assessment_year"],
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            fsi_entries=[FsiEntryRequest(**asdict(i)) for i in fsi_items],
            a3_entries=[A3EntryRequest(**asdict(i)) for i in a3_items],
        )

    async def list(self, skip: int, limit: int) -> SessionListResponse:
        items, total = await self._session_repository.list(skip, limit)
        summaries: list[SessionSummaryResponse] = []
        for item in items:
            _, fsi_total = await self._fsi_repository.list(item["id"], 0, 1)
            _, a3_total = await self._a3_repository.list(item["id"], 0, 1)
            summaries.append(
                SessionSummaryResponse(
                    id=item["id"],
                    name=item["name"],
                    assessment_year=item["assessment_year"],
                    created_at=item["created_at"],
                    updated_at=item["updated_at"],
                    fsi_count=fsi_total,
                    a3_count=a3_total,
                )
            )
        return SessionListResponse(items=summaries, total=total, skip=skip, limit=limit)

    async def delete(self, session_id: str) -> None:
        if not await self._session_repository.exists(session_id):
            raise NotFoundError(f"Session '{session_id}' not found")
        await self._session_repository.delete(session_id)
