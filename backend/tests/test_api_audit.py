from __future__ import annotations


def test_audit_records_lifecycle(client, applicant_payload):
    created = client.post("/api/applications", json=applicant_payload).json()
    app_id = created["id"]

    client.post(
        f"/api/applications/{app_id}/decision",
        json={"outcome": "approved", "reviewer": "reviewer@kyc.io", "note": "ok"},
    )

    global_log = client.get("/api/audit").json()
    actions = [e["action"] for e in global_log]
    assert "application.created" in actions
    assert "application.approved" in actions

    scoped = client.get(f"/api/audit?application_id={app_id}").json()
    assert all(e["application_id"] == app_id for e in scoped)
    assert scoped == sorted(scoped, key=lambda e: e["at"], reverse=True)


def test_audit_empty_by_default(client):
    resp = client.get("/api/audit")
    assert resp.status_code == 200
    assert resp.json() == []
