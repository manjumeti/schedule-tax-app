"""API tests for Schedule FSI, A3 calculate endpoints and sessions/export/dashboard."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

FSI_ENTRY = {
    "country": "United States Of America",
    "income_source": "Dividend",
    "income_amount": "1000",
    "tax_paid_outside_india": "100",
    "tax_payable_in_india": "500",
    "dtaa_rate": "10",
    "currency": "USD",
    "exchange_rate": "83",
    "assessment_year": "2025-26",
}

A3_ENTRY = {
    "country": "United States Of America",
    "entity_name": "Cisco Systems Inc",
    "entity_address": "170 West Tasman Drive San Jose CA",
    "zip_code": "95134",
    "nature_of_entity": "Company",
    "acquisition_date": "2023-01-15",
    "currency": "USD",
    "initial_investment_foreign": "100",
    "peak_investment_foreign": "150",
    "closing_balance_foreign": "120",
    "acquisition_exchange_rate": "80",
    "peak_exchange_rate": "83",
    "closing_exchange_rate": "82",
    "dtaa_article": "Article 12",
    "foreign_tax_paid": "20",
    "foreign_tax_credit_claimed": "15",
}


async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_fsi_calculate_without_session(client: AsyncClient):
    resp = await client.post("/api/v1/fsi/calculate", json={"entries": [FSI_ENTRY]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["summary"]["row_count"] == 1
    # income_inr=83000, tax_paid_inr=8300, dtaa_cap=8300 -> relief capped by
    # tax_payable_in_india (500), so net_tax = 500 - 500 = 0.
    assert body["rows"][0]["relief_claimed"] == "500"
    assert body["rows"][0]["net_tax"] == "0"


async def test_fsi_calculate_rejects_invalid_entry(client: AsyncClient):
    bad_entry = {**FSI_ENTRY, "dtaa_rate": "150"}
    resp = await client.post("/api/v1/fsi/calculate", json={"entries": [bad_entry]})
    assert resp.status_code == 422


async def test_session_save_and_reload_roundtrip(client: AsyncClient):
    save_resp = await client.post(
        "/api/v1/session/save",
        json={
            "name": "AY 2025-26 Filing",
            "assessment_year": "2025-26",
            "fsi_entries": [FSI_ENTRY],
            "a3_entries": [A3_ENTRY],
        },
    )
    assert save_resp.status_code == 200
    session_id = save_resp.json()["id"]
    assert len(save_resp.json()["fsi_entries"]) == 1

    get_resp = await client.get(f"/api/v1/session/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "AY 2025-26 Filing"

    list_resp = await client.get("/api/v1/session")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 1

    dashboard_resp = await client.get(f"/api/v1/dashboard/{session_id}")
    assert dashboard_resp.status_code == 200
    dashboard = dashboard_resp.json()
    assert dashboard["total_foreign_accounts"] == 1
    assert "Schedule FSI" in dashboard["generated_schedules"]

    csv_resp = await client.get(
        "/api/v1/export/csv", params={"session_id": session_id, "schedule": "fsi"}
    )
    assert csv_resp.status_code == 200
    assert csv_resp.headers["content-type"].startswith("text/csv")
    assert "Dividend" in csv_resp.text

    pdf_resp = await client.get("/api/v1/export/pdf", params={"session_id": session_id})
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF")

    delete_resp = await client.delete(f"/api/v1/session/{session_id}")
    assert delete_resp.status_code == 204

    get_after_delete = await client.get(f"/api/v1/session/{session_id}")
    assert get_after_delete.status_code == 404


async def test_get_missing_session_returns_404(client: AsyncClient):
    resp = await client.get("/api/v1/session/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["error_code"] == "not_found"
