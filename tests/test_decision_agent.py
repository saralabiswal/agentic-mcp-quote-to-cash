from __future__ import annotations

from decimal import Decimal

import pytest

from agents.decision_agent import DecisionAgent
from api.dependencies import Settings
from context.assembler import ContextAssembler
from context.models import Completeness, RecommendedAction, RiskTier


@pytest.mark.asyncio
async def test_expected_decisions() -> None:
    agent = DecisionAgent()
    acc1 = agent.decide(await ContextAssembler(Settings()).assemble("ACC-001"))
    assert acc1.risk_tier == RiskTier.HIGH
    assert acc1.recommended_action == RecommendedAction.RISK_ADJUSTED_RENEWAL
    assert acc1.adjusted_price == 79500
    acc2 = agent.decide(await ContextAssembler(Settings()).assemble("ACC-002"))
    assert acc2.risk_tier == RiskTier.LOW
    assert acc2.expansion_offer is not None
    acc3 = agent.decide(await ContextAssembler(Settings()).assemble("ACC-003"))
    assert acc3.risk_tier == RiskTier.CRITICAL
    assert acc3.decision_flag == "proposal_locked"
    acc4 = agent.decide(await ContextAssembler(Settings()).assemble("ACC-004"))
    assert acc4.risk_tier == RiskTier.HIGH
    assert acc4.recommended_action == RecommendedAction.SAVE_PLAY
    assert acc4.expansion_offer is None


@pytest.mark.asyncio
async def test_partial_context_requires_human_review() -> None:
    context = await ContextAssembler(Settings()).assemble("ACC-001")
    partial_context = context.model_copy(
        update={"context_completeness": Completeness.PARTIAL, "missing_sources": ["oms"]}
    )
    decision = DecisionAgent().decide(partial_context)
    assert decision.decision_flag == "requires_human_review"


@pytest.mark.asyncio
async def test_margin_floor_is_enforced() -> None:
    context = await ContextAssembler(Settings()).assemble("ACC-003")
    decision = DecisionAgent(min_margin_floor=0.05).decide(context)
    assert context.subscription is not None
    assert decision.adjusted_price >= context.subscription.arr * Decimal("0.95")
    assert decision.approval_required is True
