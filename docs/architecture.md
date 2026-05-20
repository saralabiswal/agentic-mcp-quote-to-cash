<!-- Author: Sarala Biswal -->
# Agentic MCP Quote-to-Cash Architecture

This document describes the implemented architecture for the Agentic MCP Quote-to-Cash application. It is written as a technical reference for enterprise architects, integration leads, revenue operations teams, and AI governance reviewers.

The system proves a specific enterprise pattern: an agent can make quote-to-cash renewal decisions from live commercial context while remaining independent of the underlying CRM, Order Management Systems, Subscription Management, and Install Base vendors.

## Architecture Goals

The implementation is designed around six goals:

| Goal | Architectural choice |
|---|---|
| Vendor independence | Vendor APIs are isolated behind MCP adapters selected by runtime configuration. |
| Canonical reasoning | Agents consume frozen Pydantic v2 canonical models, not vendor payloads. |
| Live commercial context | Context is assembled at decision time from CRM, CPQ, Order Management Systems, Subscription, and Install Base sources. |
| Resilient execution | Context assembly runs concurrently and returns a `UnifiedContext` even when one source fails. |
| Auditability | Context runs and agent decisions are persisted with source evidence and reasoning. |
| Presentation-ready demo | The React UI explains the flow from business problem through architecture, live context, decision, and audit trail. |

## Logical View

```text
Enterprise Source Systems
  Salesforce / Dynamics / Oracle CX
  Oracle CPQ Cloud
  Oracle FOM / Salesforce Order Management / SAP S/4HANA / Zuora / NetSuite
  Oracle Subscription Cloud / Zuora / Chargebee / Salesforce Revenue Cloud
  Oracle Install Base / Salesforce Asset Management / ServiceNow CMDB
        |
        v
MCP Adapter Layer
  mock_call for APP_MODE=demo
  real_call stub or documented vendor API path for APP_MODE=real
        |
        v
ContextAssembler
  asyncio.gather(..., return_exceptions=True)
  source normalization, conflict handling, completeness scoring
        |
        v
UnifiedContext
  frozen canonical account, opportunity, contacts, orders, subscription,
  products, activities, installed products, renewal signal, source attribution
        |
        v
DecisionAgent
  risk tier, recommended action, price adjustment, approval posture,
  expansion offer, decision flag, reasoning trace
        |
        v
Audit Store + FastAPI + React Decision Support UI
```

## Runtime Components

| Component | Responsibility | Implementation |
|---|---|---|
| FastAPI application | Hosts API routers and initializes audit persistence at startup. | `api/main.py` |
| Runtime settings | Loads `.env`, holds current stack selection, and supports runtime overrides. | `api/dependencies.py` |
| MCP factory | Selects concrete adapter implementations from provider enums. | `mcp/factory.py` |
| MCP adapters | Encapsulate vendor-specific calls and demo fixture loading. | `mcp/adapters/**` |
| Context assembler | Calls all source systems concurrently and builds the canonical context. | `context/assembler.py` |
| Normalizer | Converts raw adapter outputs into canonical domain objects. | `context/normalizer.py` |
| Conflict resolver | Resolves cross-source conflicts before decisioning. | `context/conflict_resolver.py` |
| Context validator | Classifies context completeness as complete, partial, or degraded. | `context/validator.py` |
| Renewal signal builder | Converts subscription, activity, order, and product facts into risk and upsell signals. | `agents/renewal_signal_builder.py` |
| Decision agent | Produces pricing, approval, action, flag, and reasoning output. | `agents/decision_agent.py` |
| Audit store | Persists context and decision payloads to an async SQLAlchemy database. | `audit/audit_store.py` |
| React UI | Presents the business problem, stack, live context, decision, audit, and architecture views. | `ui/src/**` |

## Adapter Strategy

The adapter layer is the main vendor-isolation boundary. Each business slot has a small interface, and every concrete adapter must return data that normalizes to the same canonical output for the same underlying account facts.

| Slot | Providers | Adapter files |
|---|---|---|
| CRM | Salesforce, Microsoft Dynamics 365, Oracle CX Sales | `mcp/adapters/crm/**` |
| CPQ | Oracle CPQ Cloud | `mcp/adapters/cpq/oracle_cpq/**` |
| Order Management Systems | Oracle FOM, Salesforce Order Management, SAP S/4HANA, Zuora Order Management, NetSuite Order Management | `mcp/adapters/oms/**` |
| Subscription Management | Oracle Subscription Cloud, Zuora Sub, Chargebee, Salesforce Revenue Cloud | `mcp/adapters/sub/**` |
| Install Base | Oracle Install Base, Salesforce Asset Management, ServiceNow CMDB | `mcp/adapters/install_base/**` |

The current implementation contains 16 concrete adapter classes:

- 3 CRM adapters
- 1 CPQ adapter
- 5 Order Management Systems adapters
- 4 Subscription adapters
- 3 Install Base adapters

### Demo Mode

`APP_MODE=demo` runs without external credentials. Adapters load account, opportunity, contact, activity, order, subscription, install-base, and product data from `seed_data/`.

This makes demo behavior deterministic and supports repeatable tests for the architectural proof: vendor changes alter source attribution and adapter path, not the canonical decision contract.

### Real Mode

`APP_MODE=real` is intentionally bounded. Each adapter has a `_real_call` path that either documents the vendor API boundary or raises `NotImplementedError` with integration guidance.

Real integration work should be completed inside adapters only. Agent logic must not import vendor clients, parse vendor payloads, or branch on vendor-specific fields.

## Configuration Model

Runtime selection is config-driven:

| Business slot | Setting | Values |
|---|---|---|
| Runtime mode | `APP_MODE` | `demo`, `real` |
| CRM | `CRM_PROVIDER` | `salesforce`, `dynamics`, `oracle_crm` |
| Order Management Systems | `OMS_PROVIDER` | `oracle_fom`, `salesforce_oms`, `sap_s4hana`, `zuora_oms`, `netsuite` |
| Subscription | `SUB_PROVIDER` | `oracle_subscription`, `zuora_sub`, `chargebee`, `salesforce_revenue` |
| Install Base | `INSTALL_BASE_PROVIDER` | `oracle_install_base`, `salesforce_asset`, `servicenow_cmdb` |
| Install Base toggle | `INSTALL_BASE_ENABLED` | `true`, `false` |
| Audit database | `DATABASE_URL` | Default: `sqlite+aiosqlite:///./audit.db` |
| Pricing guardrail | `MIN_MARGIN_FLOOR` | Default: `0.18` |
| Approval guardrail | `APPROVAL_DISCOUNT_THRESHOLD` | Default: `0.10` |

The UI updates these settings through `/settings`. Subsequent context assembly and decision runs use the updated runtime stack.

## Context Assembly Flow

`ContextAssembler` is the core integration orchestrator. It follows this sequence:

1. Build the selected CRM, CPQ, Order Management Systems, Subscription, and Install Base adapters through `MCPFactory`.
2. Call all source operations concurrently with `asyncio.gather(..., return_exceptions=True)`.
3. Capture failing source calls as missing-source evidence instead of raising.
4. Normalize successful outputs into canonical objects.
5. Resolve conflicts across sources.
6. Build a renewal signal from subscription, activity, order, product, and account facts.
7. Validate completeness.
8. Return a `UnifiedContext` in every path, including fallback paths.

The concurrent source calls are:

| Source call | Purpose |
|---|---|
| `crm.get_account(account_id)` | Account profile and health |
| `crm.get_opportunities(account_id)` | Renewal or expansion opportunity |
| `crm.get_contacts(account_id)` | Buyer and stakeholder contacts |
| `crm.get_activities(account_id, days=90)` | Recent commercial sentiment and escalation context |
| `cpq.get_product_catalog("all")` | Product and pricing catalogue |
| `cpq.get_pricing_context(account_id, [])` | CPQ pricing guardrail context |
| `oms.get_orders(account_id, months=24)` | Fulfillment and order history |
| `sub.get_subscription(account_id)` | ARR, renewal date, usage, escalation posture |
| `sub.get_renewal_signals(subscription_id)` | Subscription-side renewal signals |
| `install_base.get_installed_products(account_id)` | Entitlement and installed-product footprint |

The important behavior is failure isolation. A subscription timeout, for example, should not prevent CRM, CPQ, Order Management Systems, and Install Base evidence from being returned. The final decision can then be flagged for review instead of silently proceeding with incomplete truth.

## Canonical Domain Contract

All canonical schema objects are frozen Pydantic v2 models. This prevents accidental mutation after assembly and gives the decision layer a stable contract.

Key models:

| Model | Role |
|---|---|
| `CanonicalAccount` | Account identity, segment, value, health score, ownership, and region |
| `CanonicalOpportunity` | Renewal, expansion, or new-business opportunity |
| `CanonicalContact` | Stakeholder and buying-role information |
| `CanonicalSubscription` | ARR, renewal date, contracted products, usage health, escalation count |
| `CanonicalOrder` | Order history and fulfillment context |
| `CanonicalProduct` | Product catalogue, pricing tiers, bundle eligibility, config rules |
| `CanonicalActivity` | Recent account interactions and sentiment |
| `InstalledProduct` | Install Base or asset footprint |
| `RenewalSignal` | Risk, churn indicators, upsell propensity, expansion products, recommended action |
| `UnifiedContext` | Full assembled decision context plus provider selection, attribution, completeness, and missing sources |

`UnifiedContext` is the only context object the decision agent needs. It contains provider metadata for auditability, but the decision logic reasons over canonical business fields rather than vendor payloads.

## Decision Architecture

Decisioning is deterministic and explainable.

`RenewalSignalBuilder` calculates:

- Risk score from usage health, escalation count, renewal urgency, and negative activity sentiment.
- Risk tier using deterministic thresholds.
- Churn indicators from usage trend, escalations, late-stage risk, and sentiment.
- Upsell propensity from product eligibility, usage health, expansion history, and risk tier.
- Recommended action from risk tier and upsell propensity.

`DecisionAgent` then calculates:

- Base price from subscription ARR or account value fallback.
- Risk-adjusted price using deterministic tier multipliers.
- Margin-floor guardrail.
- Approval requirement when discount or guardrail thresholds are exceeded.
- Expansion offer when upsell propensity and product eligibility support it.
- Decision flag based on completeness and escalation posture.
- Reasoning steps for audit and UI display.

Decision flags are intentionally separate from risk tiers:

| Flag | Meaning |
|---|---|
| `none` | No governance blocker. The UI presents this as "No blocking flag." |
| `requires_human_review` | Context is partial and the recommendation needs review. |
| `proposal_locked` | Context is degraded or the account requires CSM escalation before proposal action. |

## Persistence And Audit

The audit layer uses SQLAlchemy 2.0 async with a configurable database URL.

Implemented tables:

| Table | Purpose |
|---|---|
| `context_runs` | Stores serialized `UnifiedContext` payloads by context run and account. |
| `agent_runs` | Stores serialized `AgentDecision` payloads by context run and account. |
| `conflict_records` | Schema placeholder for detailed conflict evidence. |
| `source_calls` | Schema placeholder for source-call telemetry. |

The implemented store persists context runs and agent runs. The API exposes retrieval through `/context/{context_run_id}`, `/agent/runs`, and `/audit/{context_run_id}`.

## API Architecture

| Endpoint | Architectural role |
|---|---|
| `GET /settings` | Return current runtime stack selection and guardrails. |
| `POST /settings` | Update stack selection without changing agent code. |
| `GET /readiness` | Exercise all adapter paths and report status/latency. |
| `POST /context/assemble` | Assemble, persist, and return `UnifiedContext`. |
| `GET /context/{context_run_id}` | Retrieve a stored context run. |
| `POST /context/compare` | Compare a snapshot placeholder with live context. |
| `POST /agent/run` | Assemble context, run the decision agent, persist both records. |
| `GET /agent/runs` | List stored decision runs. |
| `GET /audit/{context_run_id}` | Return context evidence and related agent runs. |
| `POST /demo/{scenario}` | Run a curated scenario from the demo catalogue. |

## UI Architecture

The React application is structured as an executive decision-support walkthrough rather than a generic admin console.

| Page | Purpose |
|---|---|
| Overview | Explains the business problem and why live context matters. |
| Demo Scenarios | Presents curated business scenarios and clear next actions. |
| Vendor Stack | Shows configurable vendor selections and adapter-slot proof. |
| Live Context | Displays the assembled canonical customer truth and source stack. |
| Decision Cockpit | Shows risk, price, recommendation, approval posture, and reasoning. |
| Audit Trail | Groups repeated decisions and exposes stored evidence. |
| Architecture | Explains the platform pattern and adapter isolation. |
| Logical Architecture | Shows the runtime flow as an SVG architecture diagram. |

The UI intentionally uses the same scenario catalogue as the demo runner so presentation flow and backend behavior stay aligned.

## Demo Scenario Matrix

| Scenario | Account | Stack pattern | Expected branch |
|---|---|---|---|
| 1 | `ACC-001` TechCorp | Salesforce + Oracle FOM + Oracle Sub | Snapshot-vs-live proof, high risk, risk-adjusted renewal |
| 2 | `ACC-002` GlobalBanking | Salesforce + Oracle FOM + Oracle Sub | Low risk, standard renewal, expansion eligible |
| 3 | `ACC-002` GlobalBanking | Dynamics + Oracle FOM + Oracle Sub | Same business decision as Scenario 2 with CRM swap |
| 4 | `ACC-003` MidwestManufacturing | Oracle CRM + SAP Order Management Systems + Zuora Sub | Critical risk, CSM escalation, proposal lock |
| 5 | `ACC-001` TechCorp | Salesforce + Zuora Order Management Systems + Chargebee | Mixed vendor stack, same account risk |
| 6 | `ACC-003` MidwestManufacturing | Simulated degraded subscription context | Partial context, human review required |
| 7 | `ACC-004` RetailCo | Salesforce + Oracle FOM + Oracle Sub | High risk, low upsell fit, save-play motion |

## Failure And Degradation Model

The architecture treats missing context as an auditable business condition, not an exception path hidden from users.

| Failure mode | System behavior |
|---|---|
| One source call fails | `asyncio.gather(..., return_exceptions=True)` captures the error, and the assembler continues. |
| CRM account is unavailable | Assembler returns a degraded fallback context with an "Unknown Account" shell. |
| Subscription context is missing | Renewal signal uses fallback behavior, and completeness can force human review. |
| Multiple critical sources fail | Context completeness becomes degraded, and proposal action is locked. |
| Adapter readiness fails | `/readiness` returns a red status for that adapter path. |

## Security And Governance Boundaries

This reference implementation keeps enterprise controls at explicit boundaries:

- Secrets are supplied through environment variables, not committed source.
- Demo mode requires no external credentials.
- Real vendor authentication belongs inside adapter `_real_call` implementations.
- Agent logic does not handle OAuth, tokens, vendor endpoints, or raw vendor payloads.
- Source attribution and missing-source evidence are included in `UnifiedContext`.
- Decision reasoning is stored with each agent run for audit review.

## Productionization Path

To move this reference pattern toward production, complete these work items:

1. Implement selected adapter `_real_call` methods with tenant-specific authentication, pagination, retry, timeout, and rate-limit handling.
2. Add structured source-call telemetry to populate `source_calls`.
3. Persist conflict-resolution detail to `conflict_records`.
4. Replace local SQLite with the enterprise managed database configured through `DATABASE_URL`.
5. Add authentication and role-based authorization to FastAPI and React.
6. Add tenant-aware secret management.
7. Add observability for adapter latency, failures, context completeness, and decision outcomes.
8. Extend CI with frontend tests and API contract tests if the app is promoted beyond reference-demo use.

## Validation Gates

The repository is wired for production-style checks:

```bash
make lint
make test
cd ui && npm run build
```

The Python test suite enforces an 80 percent coverage gate. Ruff and mypy guard style and static typing. The UI build verifies TypeScript and Vite production packaging.

## Architectural Principle To Preserve

The most important invariant is:

> Vendor changes must alter adapters and source attribution, not agent logic.

Any future enhancement should preserve that boundary. If a new vendor requires a decision-agent branch, the canonical contract is incomplete and should be extended before the agent is changed.
