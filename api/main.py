# Author: Sarala Biswal
"""FastAPI application bootstrap with router registration, CORS, and audit-store lifecycle wiring."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import get_runtime_settings
from api.routers import agent, audit, context, demo, settings
from audit.audit_store import AuditStore


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize audit persistence for the FastAPI application lifecycle."""
    runtime_settings = get_runtime_settings().current
    store = AuditStore(runtime_settings.database_url)
    await store.init()
    app.state.audit_store = store
    yield


app = FastAPI(title="Agentic MCP Quote to Cash", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(context.router)
app.include_router(agent.router)
app.include_router(audit.router)
app.include_router(demo.router)
app.include_router(settings.router)
