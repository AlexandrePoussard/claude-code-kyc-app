"""HTTP layer — thin adapters over services."""

from fastapi import APIRouter

from . import applications, audit, health, stats

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(applications.router)
api_router.include_router(audit.router)
api_router.include_router(stats.router)

__all__ = ["api_router"]
