"""Client-onboarding service: account creation and relationship-manager assignment.

The KYC stage is handled by ``services.applications``; this module picks up the
two follow-up stages (account creation, RM assignment) and enforces the stage
gates between them.
"""

from __future__ import annotations

import hashlib

from collections import Counter

from .. import audit, store
from ..domain import relationship_managers
from ..errors import (
    ApplicationNotFound,
    RelationshipManagerNotFound,
    StageNotReachable,
)
from ..models import (
    AccountInput,
    Application,
    AssignedRM,
    BankAccount,
    ManagerWithLoad,
    OnboardingStage,
    RelationshipManager,
)
from ..utils import utcnow


def _require(app_id: str) -> Application:
    app_obj = store.get(app_id)
    if not app_obj:
        raise ApplicationNotFound(app_id)
    return app_obj


def _generate_account_number(app_id: str) -> str:
    # Deterministic 10-digit account number derived from the application id.
    digest = hashlib.sha256(app_id.encode()).hexdigest()
    digits = "".join(c for c in digest if c.isdigit())[:10].ljust(10, "0")
    return f"ACCT-{digits}"


def create_account(app_id: str, payload: AccountInput) -> Application:
    app_obj = _require(app_id)
    if app_obj.stage != OnboardingStage.ACCOUNT_CREATION:
        raise StageNotReachable(
            app_id,
            required_stage=OnboardingStage.ACCOUNT_CREATION.value,
            current_stage=app_obj.stage.value,
        )

    account = BankAccount(
        account_number=_generate_account_number(app_id),
        type=payload.type,
        currency=payload.currency.upper(),
        opened_at=utcnow(),
        initial_deposit=payload.initial_deposit,
    )
    app_obj.account = account
    app_obj.stage = OnboardingStage.RM_ASSIGNMENT
    app_obj.updated_at = utcnow()

    audit.record(
        "system",
        "account.created",
        app_id,
        account_number=account.account_number,
        type=account.type.value,
        currency=account.currency,
        initial_deposit=account.initial_deposit,
    )
    return app_obj


def managers_with_load() -> list[ManagerWithLoad]:
    """Return every RM in the pool along with the number of clients assigned to them.

    Load is counted across *all* applications, regardless of stage, so a client
    that completes onboarding still shows up on their RM's caseload.
    """
    counts: Counter[str] = Counter()
    for app in store.all_apps():
        if app.relationship_manager:
            counts[app.relationship_manager.manager.id] += 1
    return [
        ManagerWithLoad(manager=m, assigned_count=counts.get(m.id, 0))
        for m in relationship_managers.all_managers()
    ]


def assign_relationship_manager(
    app_id: str, manager_id: str | None = None
) -> Application:
    app_obj = _require(app_id)
    if app_obj.stage != OnboardingStage.RM_ASSIGNMENT:
        raise StageNotReachable(
            app_id,
            required_stage=OnboardingStage.RM_ASSIGNMENT.value,
            current_stage=app_obj.stage.value,
        )

    manager: RelationshipManager
    reason: str
    if manager_id is None:
        manager, reason = relationship_managers.match(app_obj)
    else:
        picked = relationship_managers.get_by_id(manager_id)
        if picked is None:
            raise RelationshipManagerNotFound(manager_id)
        manager = picked
        reason = "manually selected by reviewer"

    app_obj.relationship_manager = AssignedRM(
        manager=manager, assigned_at=utcnow(), reason=reason
    )
    app_obj.stage = OnboardingStage.COMPLETED
    app_obj.updated_at = utcnow()

    audit.record(
        "system",
        "relationship_manager.assigned",
        app_id,
        manager_id=manager.id,
        manager_name=manager.name,
        reason=reason,
    )
    return app_obj
