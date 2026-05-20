<!-- Author: Sarala Biswal -->
# Developer Flow Walkthrough

This walkthrough explains how the implemented Quote-to-Cash MCP application runs from a developer’s point of view. It follows the actual code path rather than the planning documents.

## 1. Mental Model

The application has one core idea:

```text
UI action
  -> FastAPI endpoint
  -> runtime settings
  -> MCPFactory
  -> selected source-system adapters
  -> ContextAssembler
  -> UnifiedContext
  -> DecisionAgent
  -> AuditStore
  -> UI presentation
```

The decision agent never talks directly to Salesforce, Dynamics, Oracle, SAP, Zuora, NetSuite, Chargebee, or ServiceNow. It receives a `UnifiedContext` made from canonical Pydantic models.

## 2. Startup Flow

Backend startup begins in `api/main.py`.

1. FastAPI creates the application instance.
2. The app lifespan loads runtime settings through `get_runtime_settings()`.
3. `AuditStore` is created from `DATABASE_URL`.
4. Audit tables are initialized through SQLAlchemy async metadata creation.
5. Routers are registered for context, agent, audit, demo, settings, and readiness.

Relevant files:

| File | Role |
|---|---|
| `api/main.py` | FastAPI bootstrap and router registration |
| `api/dependencies.py` | `.env` settings and mutable runtime stack selection |
| `audit/audit_store.py` | Async audit persistence |
| `audit/models.py` | SQLAlchemy table definitions |

## 3. Runtime Settings Flow

Settings are loaded from `.env` or defaults in `api/dependencies.py`.

The important runtime selectors are:

| Selector | Purpose |
|---|---|
| `CRM_PROVIDER` | Chooses Salesforce, Dynamics, or Oracle CX Sales adapter |
| `OMS_PROVIDER` | Chooses the Order Management Systems adapter |
| `SUB_PROVIDER` | Chooses the Subscription Management adapter |
| `INSTALL_BASE_PROVIDER` | Chooses the Install Base or asset-management adapter |
| `INSTALL_BASE_ENABLED` | Enables or disables Install Base enrichment |
| `APP_MODE` | Chooses demo fixture calls or real adapter calls |

The UI updates settings through:

```text
POST /settings
```

That endpoint mutates the in-process `RuntimeSettings` object. The next context or decision run uses the new adapter stack.

## 4. Adapter Selection Flow

Adapter selection lives in `mcp/factory.py`.

When context assembly starts, `ContextAssembler` asks `MCPFactory` for these source slots:

```python
crm = factory.get_crm_server()
cpq = factory.get_cpq_server()
oms = factory.get_oms_server()
sub = factory.get_sub_server()
install_base = factory.get_install_base_server()
```

Provider mapping:

| Slot | Method | Providers |
|---|---|---|
| CRM | `get_crm_server()` | Salesforce, Dynamics, Oracle CX Sales |
| CPQ | `get_cpq_server()` | Oracle CPQ Cloud |
| Order Management Systems | `get_oms_server()` | Oracle FOM, Salesforce Order Management, SAP S/4HANA, Zuora, NetSuite |
| Subscription | `get_sub_server()` | Oracle Subscription Cloud, Zuora, Chargebee, Salesforce Revenue Cloud |
| Install Base | `get_install_base_server()` | Oracle Install Base, Salesforce Asset Management, ServiceNow CMDB |

The factory is the key proof point for vendor independence. Switching vendors changes the adapter class, not the agent.

## 5. MCP Adapter Execution Flow

Every adapter inherits the same execution pattern from `mcp/base.py`.

```text
adapter public method
  -> _call_tool(tool_name, params)
  -> APP_MODE check
  -> _mock_call(...) or _real_call(...)
  -> timeout wrapper
  -> normalized exception type
```

In demo mode:

- `_mock_call` loads deterministic data from `seed_data/`.
- No external credentials are required.
- The same underlying account facts can be represented through multiple vendor-shaped payloads.

In real mode:

- `_real_call` is the boundary for vendor API integration.
- Real credentials must come from environment settings.
- Adapter output must still normalize into the same canonical schema.

## 6. Context Assembly Flow

The main orchestration code is `context/assembler.py`.

For a request like:

```text
POST /context/assemble
```

or:

```text
POST /agent/run
```

the assembler performs these steps:

1. Resolve selected adapters through `MCPFactory`.
2. Call CRM, CPQ, Order Management Systems, Subscription, and Install Base sources concurrently.
3. Use `asyncio.gather(..., return_exceptions=True)` so one source failure does not fail the whole run.
4. Convert exceptions into `missing_sources`.
5. Normalize successful source outputs.
6. Resolve conflicts.
7. Build renewal signals.
8. Validate context completeness.
9. Return a `UnifiedContext`.

The concurrent calls are:

| Call | Output |
|---|---|
| `crm.get_account(account_id)` | Account profile |
| `crm.get_opportunities(account_id)` | Renewal opportunity |
| `crm.get_contacts(account_id)` | Stakeholders |
| `crm.get_activities(account_id, days=90)` | Recent activity and sentiment |
| `cpq.get_product_catalog("all")` | Product catalogue |
| `cpq.get_pricing_context(account_id, [])` | Pricing guardrail context |
| `oms.get_orders(account_id, months=24)` | Order history |
| `sub.get_subscription(account_id)` | Subscription and ARR |
| `sub.get_renewal_signals(subscription_id)` | Subscription-side renewal signals |
| `install_base.get_installed_products(account_id)` | Installed products and entitlements |

Important rule: `ContextAssembler` should never raise to the caller. It returns a complete, partial, or degraded `UnifiedContext`.

## 7. Normalization Flow

Raw adapter outputs are normalized in `context/normalizer.py`.

| Normalizer method | Canonical output |
|---|---|
| `normalize_crm(...)` | `account`, `opportunity`, `contacts`, `activities` |
| `normalize_cpq(...)` | `products` |
| `normalize_oms(...)` | `orders` |
| `normalize_sub(...)` | `subscription` |
| `normalize_install_base(...)` | `installed_base` |

Mapper helpers live in `mcp/adapters/common.py` and adapter-specific mapper modules.

The architecture goal is that all providers in the same category produce identical canonical output for the same underlying account facts.

## 8. Conflict And Completeness Flow

After normalization, `ConflictResolver` applies deterministic source-of-truth rules.

Current examples:

- Install Base enriches `account.installed_base`.
- Subscription is authoritative for renewal-date conflict evidence.
- Account-value candidates can be resolved by highest value if provided.

Then `ContextValidator` classifies context quality:

| Missing-source condition | Completeness |
|---|---|
| No missing source categories | `complete` |
| One missing source category | `partial` |
| Two or more missing source categories | `degraded` |

This completeness value is later used by the decision agent to set governance flags.

## 9. Decision Flow

Decisioning is split across two files:

| File | Role |
|---|---|
| `agents/renewal_signal_builder.py` | Creates risk and renewal signals |
| `agents/decision_agent.py` | Converts signals into price, action, flag, and reasoning |

`RenewalSignalBuilder` calculates:

- Risk score
- Risk tier
- Churn indicators
- Upsell propensity
- Expansion product eligibility
- Recommended sales motion
- Risk-adjusted pricing recommendation

`DecisionAgent` calculates:

- Base price
- Adjusted price
- Discount percentage
- Margin guardrail result
- Approval requirement
- Expansion offer
- Decision flag
- Reasoning steps

Decision flags:

| Flag | Meaning |
|---|---|
| `none` | No blocking governance condition |
| `requires_human_review` | Context is partial |
| `proposal_locked` | Context is degraded or critical escalation is required |

## 10. Audit Flow

Audit persistence is handled by `AuditStore`.

During `POST /agent/run`:

1. The API assembles context.
2. The API runs `DecisionAgent`.
3. The API stores the context payload in `context_runs`.
4. The API stores the decision payload in `agent_runs`.
5. The UI can retrieve history through `/agent/runs`.
6. A specific context run can be inspected through `/audit/{context_run_id}`.

The audit payload stores full JSON snapshots of the canonical context and decision output. This keeps the demo transparent and easy to inspect.

## 11. UI Flow

The app shell is `ui/src/App.tsx`.

It owns:

- Active page
- Active demo scenario
- Decision-run trigger state
- Shared page navigation

Key UI pages:

| Page file | User-facing purpose |
|---|---|
| `ui/src/pages/About.tsx` | Business problem and solution story |
| `ui/src/pages/StackConfigurator.tsx` | Demo scenario and vendor stack selection |
| `ui/src/pages/ContextExplorer.tsx` | Live assembled context |
| `ui/src/pages/SnapshotDemo.tsx` | Decision cockpit |
| `ui/src/pages/AgentRuns.tsx` | Audit trail |
| `ui/src/pages/Architecture.tsx` | Platform architecture story |
| `ui/src/pages/LogicalArchitecture.tsx` | SVG logical architecture |

The typed API client is `ui/src/api/client.ts`.

## 12. Common Developer Paths

### Run A Decision From The UI

```text
User clicks Run Decision
  -> ui/src/pages/SnapshotDemo.tsx
  -> runAgent(account_id)
  -> POST /agent/run
  -> ContextAssembler.assemble(...)
  -> DecisionAgent.decide(...)
  -> AuditStore.save_context_run(...)
  -> AuditStore.save_agent_run(...)
  -> UI renders risk, price, action, and reasoning
```

### Change Vendors From The UI

```text
User changes a provider
  -> ui/src/pages/StackConfigurator.tsx
  -> patchSettings(...)
  -> POST /settings
  -> RuntimeSettings.update(...)
  -> next assemble/run uses new MCPFactory adapter mapping
```

### Run A Demo Scenario

```text
User selects scenario
  -> scenario state updates in App.tsx
  -> scenario account and stack are shown in UI
  -> backend demo endpoint can call DemoRunner
  -> DemoRunner creates scenario-specific Settings
  -> ContextAssembler + DecisionAgent run the same core path
```

## 13. Scenario Coverage

| Scenario | Developer purpose |
|---|---|
| 1 | Proves stale snapshot vs live context changes risk posture |
| 2 | Baseline healthy renewal and expansion offer |
| 3 | Proves CRM vendor swap without decision-agent changes |
| 4 | Proves non-Salesforce stack and proposal-lock branch |
| 5 | Proves mixed Order Management Systems and Subscription providers |
| 6 | Proves partial-context governance branch |
| 7 | Proves save-play branch for high risk and low upsell fit |

## 14. Where To Add New Behavior

| Change | Preferred location |
|---|---|
| Add a new CRM provider | New adapter package under `mcp/adapters/crm/`, update `CRMProvider`, update `MCPFactory` |
| Add a new Order Management Systems provider | New adapter package under `mcp/adapters/oms/`, update `OMSProvider`, update `MCPFactory` |
| Add a new subscription provider | New adapter package under `mcp/adapters/sub/`, update `SubProvider`, update `MCPFactory` |
| Add canonical fields | `context/models.py`, mappers, normalizer, tests, UI types |
| Change risk scoring | `agents/renewal_signal_builder.py` |
| Change pricing or flags | `agents/decision_agent.py` |
| Change audit storage | `audit/models.py` and `audit/audit_store.py` |
| Change the presentation flow | `ui/src/App.tsx` and page components |

## 15. Guardrail For Future Changes

Preserve this boundary:

```text
Vendor-specific code belongs in adapters.
Canonical business interpretation belongs in context normalization.
Decision policy belongs in agents.
Presentation belongs in React pages.
Audit persistence belongs in audit storage.
```

If a future feature requires the decision agent to branch on a vendor name, extend the canonical schema or normalizer first.
