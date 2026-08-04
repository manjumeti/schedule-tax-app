"""Dashboard summary endpoint."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_dashboard_service
from app.dto.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{session_id}", response_model=DashboardResponse)
async def get_dashboard(
    session_id: str,
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardResponse:
    return await service.get_dashboard(session_id)
