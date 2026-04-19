from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from .. import audit as audit_store
from ..models import AuditEntry

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEntry])
def list_audit(application_id: Optional[str] = None) -> list[AuditEntry]:
    return audit_store.list_entries(application_id)
