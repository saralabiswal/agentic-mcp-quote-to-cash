# Author: Sarala Biswal
from __future__ import annotations

import pytest

from agents.decision_agent import DecisionAgent
from api.dependencies import Settings
from audit.audit_store import AuditStore
from context.assembler import ContextAssembler


@pytest.mark.asyncio
async def test_audit_store_round_trip_context_and_agent_run(tmp_path) -> None:  # type: ignore[no-untyped-def]
    store = AuditStore(f"sqlite+aiosqlite:///{tmp_path / 'audit.db'}")
    await store.init()
    context = await ContextAssembler(Settings()).assemble("ACC-001")
    decision = DecisionAgent().decide(context)
    await store.save_context_run(context)
    await store.save_agent_run(decision)

    restored_context = await store.get_context_run(context.context_run_id)
    agent_runs = await store.get_agent_runs()

    assert restored_context is not None
    assert restored_context.model_dump(mode="json") == context.model_dump(mode="json")
    assert agent_runs[0]["context_run_id"] == context.context_run_id
