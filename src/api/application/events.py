from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared.http_client import HttpClient
from sqlalchemy.ext.asyncio import AsyncEngine

from api.application.dependency_stubs import (
    DbEngineDepStub,
    HttpClientDepStub,
)
from api.application.router import root_router
from api.core.database import check_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine: AsyncEngine = app.dependency_overrides[DbEngineDepStub]()
    client: HttpClient = app.dependency_overrides[HttpClientDepStub]()

    await check_db_connection(engine)
    await client.close_unused_sessions_periodically()

    async with root_router.lifespan_context(app):
        yield

    await client.close_all_sessions()
    await engine.dispose()
