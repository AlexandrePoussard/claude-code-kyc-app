from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app import audit, store
from app.main import create_app
from app.models import (
    Address,
    ApplicantInput,
    IdDocumentType,
)


@pytest.fixture(autouse=True)
def _reset_state() -> None:
    """Each test starts with an empty in-memory store and audit log."""
    store.clear()
    audit.clear()
    yield
    store.clear()
    audit.clear()


@pytest.fixture
def client() -> TestClient:
    """TestClient without lifespan, so the seed-on-startup hook does NOT fire."""
    return TestClient(create_app())


@pytest.fixture
def applicant_factory() -> Any:
    """Build an ApplicantInput with sensible defaults. Override any field via kwargs."""

    def _make(**overrides: Any) -> ApplicantInput:
        base = dict(
            first_name="Test",
            last_name="Person",
            email="test.person@example.com",
            date_of_birth=date(1990, 5, 15),
            nationality="FR",
            address=Address(
                line1="1 Rue de Test", city="Paris", postal_code="75001", country="FR"
            ),
            id_document_type=IdDocumentType.PASSPORT,
            id_document_number="FRA-000001",
            politically_exposed=False,
        )
        base.update(overrides)
        return ApplicantInput(**base)

    return _make


@pytest.fixture
def applicant_payload() -> dict:
    """A plain dict matching ApplicantInput for POST /api/applications tests."""
    return {
        "first_name": "Test",
        "last_name": "Person",
        "email": "test.person@example.com",
        "date_of_birth": "1990-05-15",
        "nationality": "FR",
        "address": {
            "line1": "1 Rue de Test",
            "city": "Paris",
            "postal_code": "75001",
            "country": "FR",
        },
        "id_document_type": "passport",
        "id_document_number": "FRA-000001",
        "politically_exposed": False,
    }
