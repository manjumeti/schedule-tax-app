"""CSV / PDF export endpoints."""
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.api.deps import get_export_service
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/csv")
async def export_csv(
    session_id: str,
    schedule: Literal["fsi", "a3"],
    service: Annotated[ExportService, Depends(get_export_service)],
) -> Response:
    filename, content = await service.export_csv(session_id, schedule)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/pdf")
async def export_pdf(
    session_id: str,
    service: Annotated[ExportService, Depends(get_export_service)],
) -> Response:
    filename, content = await service.export_pdf(session_id)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
