"""Request DTOs for export endpoints."""
from typing import Literal

from pydantic import BaseModel


class ExportRequest(BaseModel):
    session_id: str
    schedule: Literal["fsi", "fa", "a3"]
