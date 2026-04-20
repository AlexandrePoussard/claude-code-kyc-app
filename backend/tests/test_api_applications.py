from __future__ import annotations

from io import BytesIO


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_application(client, applicant_payload):
    resp = client.post("/api/applications", json=applicant_payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["risk"]["level"] in {"low", "medium", "high"}
    assert body["sanctions"]["clear"] is True


def test_list_applications_supports_filters(client, applicant_payload):
    client.post("/api/applications", json=applicant_payload)

    pep_payload = {**applicant_payload, "email": "pep@example.com", "politically_exposed": True}
    client.post("/api/applications", json=pep_payload)

    resp_all = client.get("/api/applications")
    assert resp_all.status_code == 200
    assert len(resp_all.json()) == 2

    resp_medium = client.get("/api/applications?risk=medium")
    assert [a["applicant"]["email"] for a in resp_medium.json()] == ["pep@example.com"]

    resp_q = client.get("/api/applications?q=test.person")
    assert len(resp_q.json()) == 1


def test_list_applications_supports_stage_filter(client, applicant_payload):
    # two at stage=kyc, one at stage=account_creation (after approval)
    a1 = client.post("/api/applications", json=applicant_payload).json()
    client.post(
        "/api/applications",
        json={**applicant_payload, "email": "second@example.com"},
    )
    client.post(
        f"/api/applications/{a1['id']}/decision",
        json={"outcome": "approved", "reviewer": "reviewer@kyc.io", "note": "ok"},
    )

    kyc = client.get("/api/applications?stage=kyc").json()
    assert len(kyc) == 1
    assert kyc[0]["applicant"]["email"] == "second@example.com"

    acct = client.get("/api/applications?stage=account_creation").json()
    assert len(acct) == 1
    assert acct[0]["applicant"]["email"] == applicant_payload["email"]


def test_get_application_404(client):
    resp = client.get("/api/applications/does-not-exist")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_upload_document_transitions_to_in_review(client, applicant_payload):
    created = client.post("/api/applications", json=applicant_payload).json()
    app_id = created["id"]

    files = {"file": ("scan.jpg", BytesIO(b"x" * 512), "image/jpeg")}
    data = {"doc_type": "passport"}
    resp = client.post(f"/api/applications/{app_id}/documents", files=files, data=data)
    assert resp.status_code == 200
    body = resp.json()
    assert body["document"]["size_bytes"] == 512
    assert body["ocr_extracted"]["document_number"] == applicant_payload["id_document_number"]

    updated = client.get(f"/api/applications/{app_id}").json()
    assert updated["status"] == "in_review"
    assert len(updated["documents"]) == 1


def test_liveness_check_records_result(client, applicant_payload):
    created = client.post("/api/applications", json=applicant_payload).json()
    app_id = created["id"]

    resp = client.post(f"/api/applications/{app_id}/liveness")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) >= {"passed", "confidence", "challenge", "checked_at"}

    updated = client.get(f"/api/applications/{app_id}").json()
    assert updated["liveness"]["confidence"] == body["confidence"]


def test_rerun_sanctions(client, applicant_payload):
    created = client.post("/api/applications", json=applicant_payload).json()
    app_id = created["id"]
    resp = client.post(f"/api/applications/{app_id}/sanctions")
    assert resp.status_code == 200
    assert resp.json()["clear"] is True


def test_decision_approves(client, applicant_payload):
    created = client.post("/api/applications", json=applicant_payload).json()
    app_id = created["id"]

    resp = client.post(
        f"/api/applications/{app_id}/decision",
        json={"outcome": "approved", "reviewer": "reviewer@kyc.io", "note": "LGTM"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "approved"
    assert body["decision"]["reviewer"] == "reviewer@kyc.io"


def test_decision_cannot_be_overwritten(client, applicant_payload):
    created = client.post("/api/applications", json=applicant_payload).json()
    app_id = created["id"]
    first = client.post(
        f"/api/applications/{app_id}/decision",
        json={"outcome": "approved", "reviewer": "r1", "note": "ok"},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/applications/{app_id}/decision",
        json={"outcome": "rejected", "reviewer": "r2", "note": "nope"},
    )
    assert second.status_code == 409


def test_upload_on_unknown_application_404(client):
    files = {"file": ("scan.jpg", BytesIO(b"x" * 64), "image/jpeg")}
    data = {"doc_type": "passport"}
    resp = client.post("/api/applications/does-not-exist/documents", files=files, data=data)
    assert resp.status_code == 404
