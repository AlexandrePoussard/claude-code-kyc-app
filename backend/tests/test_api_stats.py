from __future__ import annotations


def _create(client, payload):
    return client.post("/api/applications", json=payload).json()


def test_stats_shape_empty(client):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["status_counts"] == {"pending": 0, "in_review": 0, "approved": 0, "rejected": 0}
    assert body["risk_counts"] == {"low": 0, "medium": 0, "high": 0}
    assert body["sanctions_hits"] == 0
    assert len(body["submissions_last_30_days"]) == 30
    assert body["funnel"] == {"submitted": 0, "documents_uploaded": 0, "decided": 0, "approved": 0}
    assert body["top_risk_factors"] == []
    assert body["top_countries"] == []


def test_stats_reflects_created_and_decided(client, applicant_payload):
    # Create two applicants, one clean and one PEP.
    clean = _create(client, applicant_payload)
    pep = _create(client, {**applicant_payload, "email": "pep@example.com", "politically_exposed": True})

    # Approve the clean one.
    client.post(
        f"/api/applications/{clean['id']}/decision",
        json={"outcome": "approved", "reviewer": "alice@kyc.io", "note": "ok"},
    )

    body = client.get("/api/stats").json()
    assert body["total"] == 2
    assert body["status_counts"]["approved"] == 1
    assert body["status_counts"]["pending"] == 1
    assert body["risk_counts"]["medium"] == 1  # PEP
    assert body["risk_counts"]["low"] == 1

    assert body["funnel"]["submitted"] == 2
    assert body["funnel"]["decided"] == 1
    assert body["funnel"]["approved"] == 1

    factor_codes = {f["code"] for f in body["top_risk_factors"]}
    assert "pep" in factor_codes

    countries = {c["country"] for c in body["top_countries"]}
    assert "FR" in countries

    reviewers = {r["reviewer"] for r in body["reviewer_stats"]}
    assert "alice@kyc.io" in reviewers


def test_submissions_series_is_sorted_chronologically(client, applicant_payload):
    _create(client, applicant_payload)
    series = client.get("/api/stats").json()["submissions_last_30_days"]
    dates = [row["date"] for row in series]
    assert dates == sorted(dates)
