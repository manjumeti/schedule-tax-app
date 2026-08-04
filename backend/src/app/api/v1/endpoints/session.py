"""Session save/reload endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_session_service
from app.core.middleware import limiter
from app.dto.session import (
    SessionDetailResponse,
    SessionListResponse,
    SessionSaveRequest,
)
from app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["Sessions"])


@router.post("/save", response_model=SessionDetailResponse)
@limiter.limit("20/minute")
async def save_session(
    request: Request,
    payload: SessionSaveRequest,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionDetailResponse:
    """Create a new session or overwrite an existing one's entries."""
    return await service.save(payload)


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    service: Annotated[SessionService, Depends(get_session_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
) -> SessionListResponse:
    return await service.list(skip, limit)


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionDetailResponse:
    return await service.get(session_id)


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> None:
    await service.delete(session_id)
