from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import mock_data
from .api import api_router
from .errors import (
    ApplicationAlreadyDecided,
    ApplicationNotFound,
    RelationshipManagerNotFound,
    StageNotReachable,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    mock_data.seed()
    yield


def create_app() -> FastAPI:
    fast_app = FastAPI(title="KYC Workshop API", version="0.1.0", lifespan=lifespan)

    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fast_app.include_router(api_router)

    @fast_app.exception_handler(ApplicationNotFound)
    async def _not_found(_request: Request, exc: ApplicationNotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @fast_app.exception_handler(ApplicationAlreadyDecided)
    async def _already_decided(
        _request: Request, exc: ApplicationAlreadyDecided
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @fast_app.exception_handler(StageNotReachable)
    async def _stage_not_reachable(
        _request: Request, exc: StageNotReachable
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @fast_app.exception_handler(RelationshipManagerNotFound)
    async def _rm_not_found(
        _request: Request, exc: RelationshipManagerNotFound
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    return fast_app


app = create_app()
