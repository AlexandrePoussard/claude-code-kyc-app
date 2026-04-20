from __future__ import annotations


def _create(client, payload, **overrides):
    body = {**payload, **overrides}
    return client.post("/api/applications", json=body).json()


def _approve(client, app_id):
    return client.post(
        f"/api/applications/{app_id}/decision",
        json={"outcome": "approved", "reviewer": "reviewer@kyc.io", "note": "ok"},
    ).json()


def test_new_application_starts_at_kyc_stage(client, applicant_payload):
    body = _create(client, applicant_payload)
    assert body["stage"] == "kyc"
    assert body["account"] is None
    assert body["relationship_manager"] is None


def test_approval_advances_stage_to_account_creation(client, applicant_payload):
    created = _create(client, applicant_payload)
    approved = _approve(client, created["id"])
    assert approved["status"] == "approved"
    assert approved["stage"] == "account_creation"


def test_rejection_keeps_stage_at_kyc(client, applicant_payload):
    created = _create(client, applicant_payload)
    resp = client.post(
        f"/api/applications/{created['id']}/decision",
        json={"outcome": "rejected", "reviewer": "reviewer@kyc.io", "note": "no"},
    )
    assert resp.json()["stage"] == "kyc"


def test_cannot_create_account_before_approval(client, applicant_payload):
    created = _create(client, applicant_payload)
    resp = client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "checking", "currency": "EUR", "initial_deposit": 500.0},
    )
    assert resp.status_code == 409
    assert "stage 'kyc'" in resp.json()["detail"]


def test_account_creation_advances_stage(client, applicant_payload):
    created = _create(client, applicant_payload)
    _approve(client, created["id"])
    resp = client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "investment", "currency": "eur", "initial_deposit": 10000.0},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["stage"] == "rm_assignment"
    assert body["account"]["type"] == "investment"
    assert body["account"]["currency"] == "EUR"  # uppercased
    assert body["account"]["account_number"].startswith("ACCT-")


def test_cannot_create_account_twice(client, applicant_payload):
    created = _create(client, applicant_payload)
    _approve(client, created["id"])
    first = client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "checking", "currency": "EUR", "initial_deposit": 500.0},
    )
    assert first.status_code == 201
    second = client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "savings", "currency": "EUR", "initial_deposit": 100.0},
    )
    assert second.status_code == 409


def test_cannot_assign_rm_before_account_creation(client, applicant_payload):
    created = _create(client, applicant_payload)
    _approve(client, created["id"])
    resp = client.post(
        f"/api/applications/{created['id']}/relationship-manager", json={}
    )
    assert resp.status_code == 409


def test_auto_assign_rm_completes_journey(client, applicant_payload):
    created = _create(client, applicant_payload)
    _approve(client, created["id"])
    client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "investment", "currency": "EUR", "initial_deposit": 50000.0},
    )
    resp = client.post(
        f"/api/applications/{created['id']}/relationship-manager", json={}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["stage"] == "completed"
    assert body["relationship_manager"] is not None
    # Investment account → investment specialist
    assert body["relationship_manager"]["manager"]["specialization"] == "investment"


def test_manual_rm_selection(client, applicant_payload):
    created = _create(client, applicant_payload)
    _approve(client, created["id"])
    client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "checking", "currency": "EUR", "initial_deposit": 100.0},
    )
    resp = client.post(
        f"/api/applications/{created['id']}/relationship-manager",
        json={"manager_id": "rm-006"},  # Thomas Müller, retail, de/en
    )
    assert resp.status_code == 201
    assert resp.json()["relationship_manager"]["manager"]["id"] == "rm-006"
    assert resp.json()["relationship_manager"]["reason"] == "manually selected by reviewer"


def test_manual_rm_selection_404_on_unknown_id(client, applicant_payload):
    created = _create(client, applicant_payload)
    _approve(client, created["id"])
    client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "checking", "currency": "EUR", "initial_deposit": 100.0},
    )
    resp = client.post(
        f"/api/applications/{created['id']}/relationship-manager",
        json={"manager_id": "rm-does-not-exist"},
    )
    assert resp.status_code == 404


def test_list_relationship_managers_includes_load(client):
    resp = client.get("/api/relationship-managers")
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) >= 4
    assert {e["manager"]["specialization"] for e in entries} >= {
        "retail",
        "wealth",
        "investment",
        "compliance",
    }
    # Empty store → everyone has zero caseload.
    assert all(e["assigned_count"] == 0 for e in entries)


def test_rm_workload_increments_after_assignment(client, applicant_payload):
    created = _create(client, applicant_payload)
    _approve(client, created["id"])
    client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "checking", "currency": "EUR", "initial_deposit": 100.0},
    )
    assigned = client.post(
        f"/api/applications/{created['id']}/relationship-manager", json={}
    ).json()
    chosen_id = assigned["relationship_manager"]["manager"]["id"]

    entries = client.get("/api/relationship-managers").json()
    by_id = {e["manager"]["id"]: e["assigned_count"] for e in entries}
    assert by_id[chosen_id] == 1


def test_high_risk_profile_routes_to_compliance(client, applicant_payload):
    # Country IR forces high-risk; age, PEP or other factors would also work.
    payload = {
        **applicant_payload,
        "email": "high.risk@example.com",
        "address": {**applicant_payload["address"], "country": "IR"},
    }
    created = _create(client, payload)
    _approve(client, created["id"])
    client.post(
        f"/api/applications/{created['id']}/account",
        json={"type": "checking", "currency": "EUR", "initial_deposit": 100.0},
    )
    resp = client.post(
        f"/api/applications/{created['id']}/relationship-manager", json={}
    )
    assert resp.json()["relationship_manager"]["manager"]["specialization"] == "compliance"


def test_stats_exposes_stage_counts(client, applicant_payload):
    _create(client, applicant_payload)
    body = client.get("/api/stats").json()
    assert "stage_counts" in body
    assert body["stage_counts"]["kyc"] == 1
    assert body["stage_counts"]["completed"] == 0
