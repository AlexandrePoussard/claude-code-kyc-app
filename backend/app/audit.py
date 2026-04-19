from __future__ import annotations

from typing import Optional

from .models import AuditEntry

_LOG: list[AuditEntry] = []


def record(actor: str, action: str, application_id: Optional[str] = None, **details) -> AuditEntry:
    entry = AuditEntry(
        actor=actor, action=action, application_id=application_id, details=details
    )
    _LOG.append(entry)
    return entry


def list_entries(application_id: Optional[str] = None) -> list[AuditEntry]:
    if application_id is None:
        return list(reversed(_LOG))
    return [e for e in reversed(_LOG) if e.application_id == application_id]


def clear() -> None:
    _LOG.clear()
