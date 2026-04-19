from __future__ import annotations

from fastapi import APIRouter

from ..models import StatsResponse
from ..services import stats as service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats() -> StatsResponse:
    return service.compute()
