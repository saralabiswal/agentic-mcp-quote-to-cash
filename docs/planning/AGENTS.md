# Agents — agentic-mcp-crm-integration

Agent definitions, logic, and interaction patterns.

---

## Agent Inventory

| Component | File | Type | Role |
|---|---|---|---|
| ContextAssembler | context/assembler.py | Orchestrator | Concurrent pull from all 14 adapters → UnifiedContext |
| RenewalSignalBuilder | agents/renewal_signal_builder.py | Deterministic | Risk score + churn indicators + upsell propensity |
| DecisionAgent | agents/decision_agent.py | Deterministic + Guardrailed | Renewal decision + pricing on UnifiedContext |

**No LLM in core decision path.** All decisions are deterministic and auditable.
LLM may optionally be added as a narrative layer on top of AgentDecision output
(to explain the decision in plain language) — but pricing and risk calculations
are never delegated to a non-deterministic model.

---

## ContextAssembler

**Type:** Orchestrator

**Purpose:**
Assemble a complete UnifiedContext from all configured source systems concurrently.
Never decides. Only assembles facts.

**Inputs:**
```python
account_id: str
force_refresh: bool = False
```

**Full Process:**
```python
async def assemble(self, account_id: str) -> UnifiedContext:

    # Step 1: Get all active adapters from MCPFactory
    crm    = factory.get_crm_server()
    cpq    = factory.get_cpq_server()
    oms    = factory.get_oms_server()
    sub    = factory.get_sub_server()
    ib     = factory.get_install_base_server()

    # Step 2: Pull all 5 sources concurrently
    results = await asyncio.gather(
        crm.get_account(account_id),
        crm.get_opportunities(account_id),
        crm.get_contacts(account_id),
        crm.get_activities(account_id, days=90),
        cpq.get_product_catalog(account.segment),
        cpq.get_pricing_context(account_id, subscription.contracted_products),
        oms.get_orders(account_id, months=24),
        sub.get_subscription(account_id),
        sub.get_renewal_signals(subscription.subscription_id),
        ib.get_installed_products(account_id),
        return_exceptions=True
    )

    # Step 3: Separate successes from failures
    # MCPTimeoutError or MCPConnectionError → add source to missing_sources
    # All other exceptions → log + add to missing_sources

    # Step 4: Normalize each successful result
    # Normalizer delegates to the active adapter's mapper

    # Step 5: Conflict resolution (only if multiple CRM sources would disagree
    # — in single-CRM mode, mainly resolves CRM vs Subscription date conflicts)

    # Step 6: Build RenewalSignal
    renewal_signal = RenewalSignalBuilder.build(
        subscription, activities, orders, cpq_products
    )

    # Step 7: Validate completeness
    completeness = ContextValidator.validate(assembled_context)

    # Step 8: Build source_attribution dict
    # Maps each field path → SourceAttribution{source, retrieved_at}

    # Step 9: Return UnifiedContext — never raises
    return UnifiedContext(
        context_run_id=f"CTX-{uuid4()}",
        assembled_at=datetime.utcnow(),
        crm_provider=settings.crm_provider,
        oms_provider=settings.oms_provider,
        sub_provider=settings.sub_provider,
        ...all canonical objects...,
        source_attribution=attribution,
        conflict_resolutions=resolutions,
        context_completeness=completeness,
        missing_sources=missing
    )
```

**Timeout behavior:**
- Per-source: settings.mcp_timeout_seconds (default 5s)
- Total assembly: settings.context_assembly_timeout_seconds (default 10s)
- If total exceeded: return whatever was assembled as DEGRADED

**Completeness rules:**
```
COMPLETE:  all 5 sources (CRM + CPQ + OMS + Sub + InstallBase) responded
PARTIAL:   1-2 non-critical sources failed (e.g., InstallBase or OMS)
DEGRADED:  3+ sources failed OR subscription source specifically failed
           (subscription failure = DEGRADED regardless of other sources)
```

**Hard constraints:**
- Never call MCP adapters sequentially — always asyncio.gather()
- Never let one source failure block other sources
- Never raise — always return UnifiedContext
- Always populate source_attribution for every field

---

## RenewalSignalBuilder

**Type:** Deterministic computation

**Purpose:**
Build a RenewalSignal from normalized subscription, activity, and order data.
Same inputs always produce same outputs. No external calls.

**Inputs:**
```python
subscription: CanonicalSubscription | None
activities: list[CanonicalActivity]        # last 90 days
orders: list[CanonicalOrder]               # last 24 months
cpq_products: list[CanonicalProduct]       # from CPQ catalog
account: CanonicalAccount
```

**Risk Score Formula:**
```python
# Inputs normalized to 0.0–1.0
usage_component     = 1.0 - subscription.usage_health_score        # high = bad
escalation_raw      = min(escalation_count_90d / 5.0, 1.0)        # 5+ = max risk
escalation_component= escalation_raw
urgency_raw         = max(0, (90 - days_to_renewal) / 90)         # <90 days = increasing
urgency_component   = urgency_raw
negative_count      = sum(1 for a in activities if a.sentiment == Sentiment.NEGATIVE)
sentiment_component = min(negative_count / len(activities), 1.0) if activities else 0.0

risk_score = (
    usage_component     * 0.40 +
    escalation_component* 0.25 +
    urgency_component   * 0.20 +
    sentiment_component * 0.15
)
risk_score = max(0.0, min(1.0, risk_score))
```

**Risk Tiers:**
```
risk_score >= 0.75 → CRITICAL
risk_score >= 0.50 → HIGH
risk_score >= 0.25 → MEDIUM
else               → LOW
```

**Churn Indicator Rules:**
```python
if subscription.usage_trend == UsageTrend.CRITICAL:
    ChurnIndicator("usage_critical", "high",
        f"Usage at {usage_health_score:.0%} of baseline — critical level")

if subscription.usage_trend == UsageTrend.DECLINING:
    ChurnIndicator("usage_declining", "medium",
        "Usage declining over last 90 days")

if escalation_count_90d >= 3:
    ChurnIndicator("multiple_escalations", "high",
        f"{escalation_count_90d} escalations in last 90 days")

if escalation_count_90d >= 1:
    ChurnIndicator("has_escalations", "medium",
        f"{escalation_count_90d} escalation(s) in last 90 days")

if days_to_renewal <= 30 and risk_score >= 0.50:
    ChurnIndicator("late_stage_risk", "high",
        f"High-risk account with only {days_to_renewal} days to renewal")

if sentiment_component > 0.40:
    ChurnIndicator("negative_sentiment_trend", "medium",
        f"{sentiment_component:.0%} of recent interactions show negative sentiment")
```

**Upsell Propensity Formula:**
```python
# Base: high usage = good upsell signal
base = subscription.usage_health_score

# Expansion recency boost
if last_expansion_date:
    months_since = (date.today() - last_expansion_date).days / 30
    expansion_boost = 0.0 if months_since < 6 else (0.1 if months_since < 18 else 0.2)
else:
    expansion_boost = 0.2  # never expanded = high propensity

# Product gap boost
eligible = [p for p in cpq_products
            if p.product_id not in subscription.contracted_products
            and p.is_active
            and any(b in subscription.contracted_products for b in p.bundle_eligibility)]
product_gap_boost = min(len(eligible) * 0.05, 0.2)

upsell_propensity = min(base + expansion_boost + product_gap_boost, 1.0)

# Critical risk suppresses upsell: don't push expansion on a churn risk
if risk_tier == RiskTier.CRITICAL:
    upsell_propensity = max(0.1, upsell_propensity * 0.25)
```

**Recommended Action Matrix:**
```
CRITICAL                                    → escalate_to_csm
HIGH   + upsell_propensity < 0.40          → save_play
HIGH   + upsell_propensity >= 0.40         → risk_adjusted_renewal
MEDIUM                                      → risk_adjusted_renewal
LOW    + upsell_propensity >= 0.65         → standard_renewal (+ expansion_offer)
LOW    + upsell_propensity < 0.65          → standard_renewal
```

**PricingRecommendation:**
```python
risk_multipliers = {
    RiskTier.CRITICAL: 0.88,   # 12% risk discount
    RiskTier.HIGH:     0.93,   # 7% risk discount
    RiskTier.MEDIUM:   0.97,   # 3% risk discount
    RiskTier.LOW:      1.00,   # no discount
}

base_price    = cpq_pricing_context.list_price_for_arr(subscription.arr)
adjusted      = base_price * risk_multipliers[risk_tier]
max_discount  = (base_price - adjusted) / base_price

PricingRecommendation(
    base_price=base_price,
    risk_adjusted_price=adjusted,
    max_discount_pct=max_discount,
    rationale=f"{risk_tier.value} risk — {max_discount:.0%} risk adjustment applied"
)
```

**Null handling:**
- subscription is None → risk_score=0.5, risk_tier=MEDIUM, recommended_action=standard_renewal
- activities empty → sentiment_component=0.0, escalation_count_90d=0
- orders empty → no expansion history signal

---

## DecisionAgent

**Type:** Deterministic + Guardrailed

**Purpose:**
Make a concrete, auditable renewal and pricing decision from UnifiedContext.
Enforce margin guardrails. Generate human-readable reasoning steps.

**Inputs:**
```python
context: UnifiedContext
```

**Full Decision Process:**
```python
def decide(self, context: UnifiedContext) -> AgentDecision:

    # Step 1: Confidence from context completeness
    confidence = context.context_completeness.value  # complete|partial|degraded

    # Step 2: Get renewal signal
    signal = RenewalSignalBuilder.build(
        context.subscription,
        context.activities,
        context.orders,
        context.renewal_signal   # pre-built if assembler ran it
    )

    # Step 3: Get CPQ pricing context
    cpq_pricing = get_cpq_pricing_for_account(context)
    base_price  = cpq_pricing.list_price_for_arr(context.subscription.arr)

    # Step 4: Apply risk adjustment
    risk_multiplier = {
        RiskTier.CRITICAL: 0.88,
        RiskTier.HIGH:     0.93,
        RiskTier.MEDIUM:   0.97,
        RiskTier.LOW:      1.00,
    }[signal.risk_tier]
    adjusted_price = base_price * Decimal(str(risk_multiplier))

    # Step 5: Margin guardrail — HARD, never bypassed
    min_price = base_price * Decimal(str(1 - cpq_pricing.max_discount_pct))
    guardrail_triggered = False
    if adjusted_price < min_price:
        adjusted_price = min_price
        guardrail_triggered = True

    # Step 6: Approval check
    discount_pct = float((base_price - adjusted_price) / base_price)
    approval_required = (
        discount_pct > cpq_pricing.approval_discount_threshold or
        guardrail_triggered
    )

    # Step 7: Expansion offer
    expansion_offer = None
    if signal.upsell_propensity > 0.65 and signal.expansion_products:
        best_product = get_best_expansion_product(
            signal.expansion_products, cpq_pricing, context.account.segment
        )
        expansion_offer = ExpansionOffer(
            product_id=best_product.product_id,
            product_name=best_product.name,
            expansion_price=best_product.pricing_tiers[0].list_price,
            rationale=f"Upsell propensity {signal.upsell_propensity:.2f} — "
                      f"{best_product.name} eligible based on current subscription"
        )

    # Step 8: Set decision flags
    decision_flag = "none"
    if context.context_completeness == Completeness.PARTIAL:
        decision_flag = "requires_human_review"
    elif context.context_completeness == Completeness.DEGRADED:
        decision_flag = "proposal_locked"
    elif signal.recommended_action == RecommendedAction.ESCALATE_TO_CSM:
        decision_flag = "proposal_locked"   # CSM must make contact first

    # Step 9: Build reasoning steps
    reasoning_steps = build_reasoning_steps(context, signal, base_price,
                                             adjusted_price, approval_required,
                                             expansion_offer)

    return AgentDecision(
        context_run_id=context.context_run_id,
        account_id=context.account.canonical_account_id,
        risk_score=signal.risk_score,
        risk_tier=signal.risk_tier,
        recommended_action=signal.recommended_action,
        base_price=base_price,
        adjusted_price=adjusted_price,
        discount_pct=discount_pct,
        margin_pct=float(adjusted_price / base_price - Decimal("1")),
        approval_required=approval_required,
        approval_reason=build_approval_reason(...) if approval_required else None,
        expansion_offer=expansion_offer,
        confidence=confidence,
        decision_flag=decision_flag,
        reasoning_steps=reasoning_steps,
        created_at=datetime.utcnow()
    )
```

**Reasoning Steps (always populated):**
```python
def build_reasoning_steps(...) -> list[str]:
    return [
        f"Context: {crm_provider.value} CRM + {oms_provider.value} OMS + "
        f"{sub_provider.value} Sub | completeness: {completeness.value}",
        f"Missing sources: {missing_sources or 'none'}",
        f"Account: {account.name} ({account.segment.value}), "
        f"health_score: {health_score:.2f}",
        f"Subscription ARR: ${arr:,.0f} | status: {status.value} | "
        f"renewal in {days_to_renewal} days ({urgency_tier.value})",
        f"Usage health: {usage_health_score:.2f} | trend: {usage_trend.value}",
        f"Escalations (90d): {escalation_count_90d}",
        f"Churn indicators: {[i.indicator_type for i in churn_indicators] or 'none'}",
        f"Risk score: {risk_score:.3f} → tier: {risk_tier.value}",
        f"Base price: ${base_price:,.0f}",
        f"Risk multiplier: {risk_multiplier:.0%} → adjusted: ${adjusted_price:,.0f}",
        f"Margin guardrail: {'TRIGGERED — clamped to floor' if guardrail_triggered else 'passed'}",
        f"Approval required: {approval_required}"
        + (f" ({approval_reason})" if approval_required else ""),
        f"Upsell propensity: {upsell_propensity:.2f}"
        + (" → expansion offer included" if expansion_offer else ""),
        f"Recommended action: {recommended_action.value}",
        f"Decision flag: {decision_flag}",
    ]
```

**AgentDecision model:**
```python
class AgentDecision(BaseModel):
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
    confidence: str            # complete | partial | degraded
    decision_flag: str         # none | requires_human_review | proposal_locked
    reasoning_steps: list[str]
    created_at: datetime

class ExpansionOffer(BaseModel):
    product_id: str
    product_name: str
    expansion_price: Decimal
    rationale: str
```

**Hard Guardrails — never bypassed regardless of context:**
1. adjusted_price never below min_margin_floor (clamped, not rejected)
2. discount > threshold ALWAYS sets approval_required = True
3. DEGRADED context ALWAYS sets decision_flag = proposal_locked
4. escalate_to_csm ALWAYS sets decision_flag = proposal_locked

---

## Interaction Flow

```
POST /agent/run (account_id)
        │
        ▼
ContextAssembler.assemble(account_id)
        │
        ├── asyncio.gather(10 concurrent MCP calls):
        │       crm.get_account()
        │       crm.get_opportunities()
        │       crm.get_contacts()
        │       crm.get_activities()
        │       cpq.get_product_catalog()
        │       cpq.get_pricing_context()
        │       oms.get_orders()
        │       sub.get_subscription()
        │       sub.get_renewal_signals()
        │       install_base.get_installed_products()
        │
        ├── Normalizer (delegates to active adapter mapper)
        ├── ConflictResolver
        ├── RenewalSignalBuilder.build()
        ├── ContextValidator.validate()
        └── UnifiedContext returned
                │
                ▼
        DecisionAgent.decide(context)
                │
                ├── Risk score computation
                ├── Pricing calculation
                ├── Margin guardrail enforcement
                ├── Expansion offer check
                ├── Decision flag setting
                ├── Reasoning steps construction
                └── AgentDecision returned
                        │
                        ▼
                AuditStore.save_agent_run()
                        │
                        ▼
                Return AgentDecision to caller
```

---

## Vendor Swap Pattern

Swapping any vendor requires ONLY a config change. Zero agent code changes.

```bash
# Example: switch from Salesforce to Dynamics
curl -X POST /settings -d '{"crm_provider": "dynamics"}'

# Next /agent/run call automatically:
# - MCPFactory returns DynamicsMCP instead of SalesforceMCP
# - DynamicsMapper normalizes Dynamics schema → same CanonicalAccount
# - All downstream agents receive identical UnifiedContext
# - AgentDecision output is identical

# Example: switch to SAP OMS + Chargebee Sub
curl -X POST /settings -d '{"oms_provider": "sap_s4hana", "sub_provider": "chargebee"}'
```

This is the core architectural proof: **The agent is truly vendor-agnostic.**

---

## Extending the System

### Adding a new CRM adapter:
1. Create mcp/adapters/crm/your_crm/your_crm_mcp.py extending AbstractCRMServer
2. Implement _mock_call with seed_data/ fixture loading
3. Implement _real_call with documented API calls (or NotImplementedError stub)
4. Create your_crm_mapper.py → canonical objects
5. Add CRMProvider.YOUR_CRM to enum
6. Add to MCPFactory.get_crm_server() dispatch dict
7. Add seed data for all 3 accounts in your CRM's schema
8. Write tests

### Adding a new OMS / Sub adapter:
Same pattern. Implement AbstractOMSServer or AbstractSubServer.
Add to OMSProvider / SubProvider enum and MCPFactory dispatch.

**Agent layer requires zero changes.**
