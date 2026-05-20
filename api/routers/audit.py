# Author: Sarala Biswal
"""Audit API router for retrieving persisted context and related agent decision records."""
from __future__ import annotations

from typing import cast

from fastapi import APIRouter, HTTPException, Request

from audit.audit_store import AuditStore

router = APIRouter()


@router.get("/audit/{context_run_id}")
async def get_audit(context_run_id: str, request: Request) -> dict[str, object]:
    """Return persisted context evidence and matching agent decisions."""
    store = cast(AuditStore, request.app.state.audit_store)
    context = await store.get_context_run(context_run_id)
    if context is None:
        raise HTTPException(status_code=404, detail="context run not found")
    agent_runs = await store.get_agent_runs()
    return {
        "context": context,
        "agent_runs": [run for run in agent_runs if run["context_run_id"] == context_run_id],
    }
