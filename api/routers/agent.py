# Author: Sarala Biswal
"""Agent API router for assembling context, running decisions, and persisting decision evidence."""
from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request
from pydantic import BaseModel

from agents.decision_agent import AgentDecision, DecisionAgent
from api.dependencies import get_runtime_settings
from audit.audit_store import AuditStore
from context.assembler import ContextAssembler

router = APIRouter()


class AgentRunRequest(BaseModel):
    """Request body for running the decision agent for an account."""

    account_id: str


@router.post("/agent/run")
async def run_agent(payload: AgentRunRequest, request: Request) -> AgentDecision:
    """Assemble context, run the decision agent, and persist both records."""
    settings = get_runtime_settings().current
    context = await ContextAssembler(settings).assemble(payload.account_id)
    decision = DecisionAgent(
        settings.min_margin_floor,
        settings.approval_discount_threshold,
    ).decide(context)
    store = cast(AuditStore, request.app.state.audit_store)
    await store.save_context_run(context)
    await store.save_agent_run(decision)
    return decision


@router.get("/agent/runs")
async def list_agent_runs(request: Request) -> list[dict[str, object]]:
    """Return persisted agent decisions for the audit trail page."""
    store = cast(AuditStore, request.app.state.audit_store)
    return await store.get_agent_runs()
