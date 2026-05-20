# Author: Sarala Biswal
from __future__ import annotations

from typing import cast

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from api.dependencies import get_runtime_settings
from audit.audit_store import AuditStore
from context.assembler import ContextAssembler
from context.models import UnifiedContext

router = APIRouter()


class AssembleRequest(BaseModel):
    account_id: str
    force_refresh: bool = False


@router.post("/context/assemble")
async def assemble_context(payload: AssembleRequest, request: Request) -> UnifiedContext:
    context = await ContextAssembler(get_runtime_settings().current).assemble(
        payload.account_id,
        payload.force_refresh,
    )
    store = cast(AuditStore, request.app.state.audit_store)
    await store.save_context_run(context)
    return context


@router.get("/context/{context_run_id}")
async def get_context(context_run_id: str, request: Request) -> UnifiedContext:
    store = cast(AuditStore, request.app.state.audit_store)
    context = await store.get_context_run(context_run_id)
    if context is None:
        raise HTTPException(status_code=404, detail="context run not found")
    return context


@router.post("/context/compare")
async def compare_context(payload: AssembleRequest, request: Request) -> dict[str, object]:
    live = await assemble_context(payload, request)
    return {"snapshot": {"risk_tier": "medium"}, "live": live}
