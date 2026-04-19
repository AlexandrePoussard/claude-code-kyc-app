from __future__ import annotations

from app.domain.liveness import run_check


def test_liveness_is_deterministic_per_email():
    a = run_check("alice@example.com")
    b = run_check("alice@example.com")
    assert a.confidence == b.confidence
    assert a.passed == b.passed
    assert a.challenge == b.challenge


def test_different_emails_can_differ():
    a = run_check("alice@example.com")
    b = run_check("zed@example.com")
    # Deterministic but seeded differently — at least one field should diverge
    assert (a.confidence, a.challenge) != (b.confidence, b.challenge)


def test_tiny_selfie_forces_failure():
    result = run_check("alice@example.com", selfie_payload=b"x")
    assert result.passed is False
    assert result.confidence <= 0.4


def test_confidence_bounds():
    result = run_check("alice@example.com")
    assert 0.0 <= result.confidence <= 1.0
