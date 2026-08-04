"""Repository-layer contracts (Repository Pattern).

Services depend only on these Protocols, never on SQLAlchemy directly, which
keeps persistence swappable and makes services trivially unit-testable with
in-memory fakes.
"""
from __future__ import annotations

from typing import Protocol

from app.domain.entities.a3 import ForeignTaxCreditDetail
from app.domain.entities.fsi import ForeignSourceIncome


class Page[T](Protocol):
    items: list[T]
    total: int


class SessionRepository(Protocol):
    async def create(self, name: str, assessment_year: str, owner_ref: str | None) -> str: ...

    async def get(self, session_id: str) -> dict | None: ...

    async def list(self, skip: int, limit: int) -> tuple[list[dict], int]: ...

    async def update_metadata(self, session_id: str, name: str, assessment_year: str) -> None: ...

    async def touch(self, session_id: str) -> None: ...

    async def delete(self, session_id: str) -> None: ...

    async def exists(self, session_id: str) -> bool: ...


class FsiRepository(Protocol):
    async def add_many(
        self, session_id: str, entries: list[ForeignSourceIncome]
    ) -> None: ...

    async def list(
        self, session_id: str, skip: int, limit: int
    ) -> tuple[list[ForeignSourceIncome], int]: ...

    async def replace_all(
        self, session_id: str, entries: list[ForeignSourceIncome]
    ) -> None: ...


class A3Repository(Protocol):
    async def add_many(
        self, session_id: str, entries: list[ForeignTaxCreditDetail]
    ) -> None: ...

    async def list(
        self, session_id: str, skip: int, limit: int
    ) -> tuple[list[ForeignTaxCreditDetail], int]: ...

    async def replace_all(
        self, session_id: str, entries: list[ForeignTaxCreditDetail]
    ) -> None: ...
