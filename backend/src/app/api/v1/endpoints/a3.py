"""Form A3 endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_a3_service
from app.core.middleware import limiter
from app.dto.a3 import (
    A3CalculateFromLotsRequest,
    A3CalculateRequest,
    A3CalculateResponse,
    A3ListResponse,
)
from app.services.a3_service import A3Service

router = APIRouter(prefix="/a3", tags=["Form A3"])


@router.post("/calculate", response_model=A3CalculateResponse)
@limiter.limit("30/minute")
async def calculate_a3(
    request: Request,
    payload: A3CalculateRequest,
    service: Annotated[A3Service, Depends(get_a3_service)],
) -> A3CalculateResponse:
    """Validate Form A3 input rows and convert investment/tax-credit values to INR."""
    return await service.calculate(payload)


@router.post("/calculate-from-lots", response_model=A3CalculateResponse)
@limiter.limit("30/minute")
async def calculate_a3_from_lots(
    request: Request,
    payload: A3CalculateFromLotsRequest,
    service: Annotated[A3Service, Depends(get_a3_service)],
) -> A3CalculateResponse:
    """Aggregate RSU/ESPP vest lots (date/cost/quantity) by acquisition date, auto-fetching
    FX rates and stock prices, and convert to Form A3 rows. Requires
    APP_MARKET_DATA_PROVIDER=yfinance_sbi."""
    return await service.calculate_from_lots(payload)


@router.get("/session/{session_id}", response_model=A3ListResponse)
async def list_a3_entries(
    session_id: str,
    service: Annotated[A3Service, Depends(get_a3_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> A3ListResponse:
    return await service.list_entries(session_id, skip, limit)
