from __future__ import annotations

from fastapi import APIRouter

from ..utils import utcnow

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "time": utcnow().isoformat()}
