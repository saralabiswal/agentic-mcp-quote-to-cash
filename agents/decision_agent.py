# Author: Sarala Biswal
"""Deterministic decision agent that turns a UnifiedContext into an auditable renewal recommendation."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict

from agents.renewal_signal_builder import RenewalSignalBuilder
from context.models import Completeness, RecommendedAction, RenewalSignal, RiskTier, UnifiedContext


class ExpansionOffer(BaseModel):
    """Optional expansion recommendation attached to a low-risk renewal."""

    model_config = ConfigDict(frozen=True)
    product_id: str
    product_name: str
    expansion_price: Decimal
    rationale: str


class AgentDecision(BaseModel):
    """Frozen decision payload returned by the API and stored in audit history."""

    model_config = ConfigDict(frozen=True)
    context_run_id: str
    account_id: str
    risk_score: float
    risk_tier: RiskTier
    recommended_action: RecommendedAction
    base_price: Decimal
    adjusted_price: Decimal
    discount_pct: float
    margin_pct: float
    approval_required: bool
    approval_reason: str | None
    expansion_offer: ExpansionOffer | None
    confidence: str
    decision_flag: str
    reasoning_steps: list[str]
    created_at: datetime


class DecisionAgent:
    """Deterministic quote-to-cash decision engine.

    The agent deliberately consumes only `UnifiedContext` and canonical
    `RenewalSignal` data. Vendor-specific differences must be resolved before
    this layer so pricing and governance behavior remains portable across
    Salesforce, Dynamics, Oracle, SAP, Zuora, NetSuite, Chargebee, and
    ServiceNow-backed stacks.
    """

    def __init__(self, min_margin_floor: float = 0.18, approval_discount_threshold: float = 0.10) -> None:
        """Configure pricing guardrails used by all decisions."""
        self.min_margin_floor = Decimal(str(min_margin_floor))
        self.approval_discount_threshold = approval_discount_threshold
        self.builder = RenewalSignalBuilder()

    def decide(self, context: UnifiedContext) -> AgentDecision:
        """Produce the renewal action, risk, pricing, and audit reasoning."""
        signal = context.renewal_signal or self.builder.build(
            context.subscription,
            context.activities,
            context.orders,
            context.products,
            context.account,
        )
        base_price = (
            context.subscription.arr
            if context.subscription is not None
            else Decimal(str(context.account.account_value))
        )
        multipliers = {
            RiskTier.CRITICAL: Decimal("0.88"),
            RiskTier.HIGH: Decimal("0.93"),
            RiskTier.MEDIUM: Decimal("0.97"),
            RiskTier.LOW: Decimal("1.00"),
        }
        adjusted = self._round_money(base_price * multipliers[signal.risk_tier])
        min_price = self._round_money(base_price * (Decimal("1") - self.min_margin_floor))
        guardrail_triggered = False
        if adjusted < min_price:
            adjusted = min_price
            guardrail_triggered = True
        discount_pct = float((base_price - adjusted) / base_price) if base_price else 0.0
        approval_required = discount_pct > self.approval_discount_threshold or guardrail_triggered
        expansion_offer = self._expansion_offer(signal, context)
        decision_flag = self._decision_flag(context, signal)
        reasoning_steps = self._reasoning_steps(
            context,
            signal,
            base_price,
            adjusted,
            approval_required,
            guardrail_triggered,
            expansion_offer,
            decision_flag,
        )
        return AgentDecision(
            context_run_id=context.context_run_id,
            account_id=context.account.canonical_account_id,
            risk_score=signal.risk_score,
            risk_tier=signal.risk_tier,
            recommended_action=signal.recommended_action,
            base_price=base_price,
            adjusted_price=adjusted,
            discount_pct=discount_pct,
            margin_pct=float(adjusted / base_price - Decimal("1")) if base_price else 0.0,
            approval_required=approval_required,
            approval_reason="discount exceeds approval threshold" if approval_required else None,
            expansion_offer=expansion_offer,
            confidence=context.context_completeness.value,
            decision_flag=decision_flag,
            reasoning_steps=reasoning_steps,
            created_at=datetime.now(timezone.utc),
        )

    def _round_money(self, value: Decimal) -> Decimal:
        """Round monetary output to the nearest hundred for presentation."""
        return (value / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * Decimal("100")

    def _expansion_offer(self, signal: RenewalSignal, context: UnifiedContext) -> ExpansionOffer | None:
        """Create an expansion offer only when risk and product eligibility allow it."""
        if signal.upsell_propensity <= 0.65 or not signal.expansion_products:
            return None
        product_id = signal.expansion_products[0]
        product = next((item for item in context.products if item.product_id == product_id), None)
        if product is None or not product.pricing_tiers:
            return None
        return ExpansionOffer(
            product_id=product.product_id,
            product_name=product.name,
            expansion_price=product.pricing_tiers[0].list_price,
            rationale=f"Upsell propensity {signal.upsell_propensity:.2f} supports expansion.",
        )

    def _decision_flag(self, context: UnifiedContext, signal: RenewalSignal) -> str:
        """Convert completeness and escalation posture into governance flags."""
        if context.context_completeness == Completeness.PARTIAL:
            return "requires_human_review"
        if context.context_completeness == Completeness.DEGRADED:
            return "proposal_locked"
        if signal.recommended_action == RecommendedAction.ESCALATE_TO_CSM:
            return "proposal_locked"
        return "none"

    def _reasoning_steps(
        self,
        context: UnifiedContext,
        signal: RenewalSignal,
        base_price: Decimal,
        adjusted: Decimal,
        approval_required: bool,
        guardrail_triggered: bool,
        expansion_offer: ExpansionOffer | None,
        decision_flag: str,
    ) -> list[str]:
        """Build human-readable reasoning for the audit trail and UI."""
        return [
            f"Context: {context.crm_provider.value} CRM + {context.oms_provider.value} OMS + {context.sub_provider.value} Sub | completeness: {context.context_completeness.value}",
            f"Missing sources: {context.missing_sources or 'none'}",
            f"Account: {context.account.name} ({context.account.segment.value}), health_score: {context.account.health_score:.2f}",
            f"Risk score: {signal.risk_score:.3f} -> tier: {signal.risk_tier.value}",
            f"Base price: ${base_price:,.0f}",
            f"Adjusted price: ${adjusted:,.0f}",
            f"Margin guardrail: {'TRIGGERED - clamped to floor' if guardrail_triggered else 'passed'}",
            f"Approval required: {approval_required}",
            f"Upsell propensity: {signal.upsell_propensity:.2f}" + (" -> expansion offer included" if expansion_offer else ""),
            f"Recommended action: {signal.recommended_action.value}",
            f"Decision flag: {decision_flag}",
        ]
