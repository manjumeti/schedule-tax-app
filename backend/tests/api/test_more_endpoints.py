"""Additional API tests for A3 calculate, list-entries pagination, and A3 CSV export."""
import pytest
from httpx import AsyncClient

from tests.api.test_endpoints import A3_ENTRY, FSI_ENTRY

pytestmark = pytest.mark.asyncio


async def test_a3_calculate_without_session(client: AsyncClient):
    resp = await client.post("/api/v1/a3/calculate", json={"entries": [A3_ENTRY]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["summary"]["row_count"] == 1
    assert body["rows"][0]["initial_investment"] == "8000"


async def test_list_entries_pagination(client: AsyncClient):
    save_resp = await client.post(
        "/api/v1/session/save",
        json={
            "name": "Pagination Filing",
            "assessment_year": "2025-26",
            "fsi_entries": [FSI_ENTRY, {**FSI_ENTRY, "income_source": "Interest"}],
        },
    )
    session_id = save_resp.json()["id"]

    page = await client.get(f"/api/v1/fsi/session/{session_id}", params={"skip": 0, "limit": 1})
    assert page.status_code == 200
    body = page.json()
    assert body["total"] == 2
    assert len(body["items"]) == 1


async def test_export_csv_for_a3(client: AsyncClient):
    save_resp = await client.post(
        "/api/v1/session/save",
        json={
            "name": "Export Filing",
            "assessment_year": "2025-26",
            "a3_entries": [A3_ENTRY],
        },
    )
    session_id = save_resp.json()["id"]

    a3_csv = await client.get(
        "/api/v1/export/csv", params={"session_id": session_id, "schedule": "a3"}
    )
    assert a3_csv.status_code == 200
    assert "Cisco Systems Inc" in a3_csv.text


async def test_export_csv_for_missing_session_returns_404(client: AsyncClient):
    resp = await client.get(
        "/api/v1/export/csv", params={"session_id": "missing", "schedule": "fsi"}
    )
    assert resp.status_code == 404


async def test_calculate_with_session_id_persists_entries(client: AsyncClient):
    save_resp = await client.post(
        "/api/v1/session/save",
        json={"name": "Attach Filing", "assessment_year": "2025-26"},
    )
    session_id = save_resp.json()["id"]

    fsi_resp = await client.post(
        "/api/v1/fsi/calculate", json={"session_id": session_id, "entries": [FSI_ENTRY]}
    )
    assert fsi_resp.status_code == 200
    assert fsi_resp.json()["session_id"] == session_id

    a3_resp = await client.post(
        "/api/v1/a3/calculate", json={"session_id": session_id, "entries": [A3_ENTRY]}
    )
    assert a3_resp.status_code == 200

    dashboard_resp = await client.get(f"/api/v1/dashboard/{session_id}")
    assert dashboard_resp.json()["validation_status"]["is_valid"] is True


async def test_calculate_with_missing_session_returns_404(client: AsyncClient):
    resp = await client.post(
        "/api/v1/fsi/calculate", json={"session_id": "missing", "entries": [FSI_ENTRY]}
    )
    assert resp.status_code == 404


async def test_dashboard_for_empty_session_reports_warning(client: AsyncClient):
    save_resp = await client.post(
        "/api/v1/session/save", json={"name": "Empty Filing", "assessment_year": "2025-26"}
    )
    session_id = save_resp.json()["id"]

    resp = await client.get(f"/api/v1/dashboard/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["validation_status"]["warning_count"] == 1
    assert resp.json()["generated_schedules"] == []


async def test_dashboard_for_missing_session_returns_404(client: AsyncClient):
    resp = await client.get("/api/v1/dashboard/missing")
    assert resp.status_code == 404


async def test_session_list_reflects_entry_counts(client: AsyncClient):
    save_resp = await client.post(
        "/api/v1/session/save",
        json={
            "name": "Counted Filing",
            "assessment_year": "2025-26",
            "fsi_entries": [FSI_ENTRY],
        },
    )
    session_id = save_resp.json()["id"]

    list_resp = await client.get("/api/v1/session")
    match = next(item for item in list_resp.json()["items"] if item["id"] == session_id)
    assert match["fsi_count"] == 1
    assert match["a3_count"] == 0


async def test_save_session_update_replaces_entries(client: AsyncClient):
    save_resp = await client.post(
        "/api/v1/session/save",
        json={"name": "Filing v1", "assessment_year": "2025-26", "fsi_entries": [FSI_ENTRY]},
    )
    session_id = save_resp.json()["id"]

    update_resp = await client.post(
        "/api/v1/session/save",
        json={
            "session_id": session_id,
            "name": "Filing v2",
            "assessment_year": "2025-26",
            "fsi_entries": [],
        },
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Filing v2"
    assert update_resp.json()["fsi_entries"] == []


async def test_save_session_update_missing_session_returns_404(client: AsyncClient):
    resp = await client.post(
        "/api/v1/session/save",
        json={"session_id": "missing", "name": "X", "assessment_year": "2025-26"},
    )
    assert resp.status_code == 404
