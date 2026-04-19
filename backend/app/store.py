from __future__ import annotations

from typing import Optional

from .models import Application

_APPLICATIONS: dict[str, Application] = {}


def put(app: Application) -> Application:
    _APPLICATIONS[app.id] = app
    return app


def get(app_id: str) -> Optional[Application]:
    return _APPLICATIONS.get(app_id)


def all_apps() -> list[Application]:
    return sorted(_APPLICATIONS.values(), key=lambda a: a.created_at, reverse=True)


def delete(app_id: str) -> bool:
    return _APPLICATIONS.pop(app_id, None) is not None


def clear() -> None:
    _APPLICATIONS.clear()
