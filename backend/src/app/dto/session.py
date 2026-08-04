"""Request/response DTOs for session save/reload."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.dto.a3 import A3EntryRequest
from app.dto.common import validate_assessment_year
from app.dto.fsi import FsiEntryRequest


class SessionSaveRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: str | None = Field(
        default=None, description="Omit to create a new session; provide to update an existing one"
    )
    name: str = Field(..., min_length=1, max_length=200)
    assessment_year: str
    owner_ref: str | None = Field(default=None, max_length=200)
    fsi_entries: list[FsiEntryRequest] = Field(default_factory=list)
    a3_entries: list[A3EntryRequest] = Field(default_factory=list)

    @field_validator("assessment_year")
    @classmethod
    def _assessment_year(cls, v: str) -> str:
        return validate_assessment_year(v)


class SessionSummaryResponse(BaseModel):
    id: str
    name: str
    assessment_year: str
    created_at: datetime
    updated_at: datetime
    fsi_count: int
    a3_count: int


class SessionDetailResponse(BaseModel):
    id: str
    name: str
    assessment_year: str
    created_at: datetime
    updated_at: datetime
    fsi_entries: list[FsiEntryRequest]
    a3_entries: list[A3EntryRequest]


class SessionListResponse(BaseModel):
    items: list[SessionSummaryResponse]
    total: int
    skip: int
    limit: int
