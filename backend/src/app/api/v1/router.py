"""Aggregates all v1 endpoint routers."""
from fastapi import APIRouter

from app.api.v1.endpoints import a3, dashboard, export, fsi, session

api_router = APIRouter()
api_router.include_router(fsi.router)
api_router.include_router(a3.router)
api_router.include_router(export.router)
api_router.include_router(session.router)
api_router.include_router(dashboard.router)
