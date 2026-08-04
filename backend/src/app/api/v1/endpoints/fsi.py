"""Schedule FSI endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_fsi_service
from app.core.middleware import limiter
from app.dto.fsi import FsiCalculateRequest, FsiCalculateResponse, FsiListResponse
from app.services.fsi_service import FsiService

router = APIRouter(prefix="/fsi", tags=["Schedule FSI"])


@router.post("/calculate", response_model=FsiCalculateResponse)
@limiter.limit("30/minute")
async def calculate_fsi(
    request: Request,
    payload: FsiCalculateRequest,
    service: Annotated[FsiService, Depends(get_fsi_service)],
) -> FsiCalculateResponse:
    """Validate FSI input rows and compute DTAA relief / net tax per Section 90/91."""
    return await service.calculate(payload)


@router.get("/session/{session_id}", response_model=FsiListResponse)
async def list_fsi_entries(
    session_id: str,
    service: Annotated[FsiService, Depends(get_fsi_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> FsiListResponse:
    return await service.list_entries(session_id, skip, limit)
