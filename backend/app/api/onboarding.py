from __future__ import annotations

from fastapi import APIRouter

from ..models import (
    AccountInput,
    Application,
    ManagerWithLoad,
    RMAssignInput,
)
from ..services import onboarding as service

router = APIRouter(tags=["onboarding"])


@router.post(
    "/applications/{app_id}/account",
    response_model=Application,
    status_code=201,
)
def create_account(app_id: str, payload: AccountInput) -> Application:
    return service.create_account(app_id, payload)


@router.post(
    "/applications/{app_id}/relationship-manager",
    response_model=Application,
    status_code=201,
)
def assign_relationship_manager(
    app_id: str, payload: RMAssignInput = RMAssignInput()
) -> Application:
    return service.assign_relationship_manager(app_id, payload.manager_id)


@router.get("/relationship-managers", response_model=list[ManagerWithLoad])
def list_relationship_managers() -> list[ManagerWithLoad]:
    return service.managers_with_load()
