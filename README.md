<!-- Author: Sarala Biswal -->
# Agentic MCP Quote-to-Cash

Enterprise-grade reference application for **vendor-agnostic quote-to-cash agentic decision support**.

The application assembles live commercial context from CRM, Oracle CPQ, Order Management Systems, Subscription Management, and Install Base systems through an MCP adapter layer. A deterministic `DecisionAgent` then produces renewal risk, pricing, approval posture, decision flags, and a complete audit trail.

The core architectural proof is simple: **vendor selection is configuration, not agent code**. Switching CRM from Salesforce to Microsoft Dynamics 365, or Order Management Systems from Oracle FOM to SAP S/4HANA, changes the adapter path and source attribution while preserving the canonical decision contract.

This is built for enterprise architects, revenue operations leaders, CPQ transformation teams, integration owners, and AI governance reviewers who need to see how an agent can make a pricing or renewal recommendation from live commercial context without becoming tightly coupled to one vendor stack.

## Business Problem

Quote-to-cash decisions are high-value, time-sensitive, and usually made from fragmented enterprise data. A renewal manager may see customer health in CRM, pricing rules in CPQ, fulfillment status in an Order Management Systems platform, usage and renewal posture in a Subscription Management platform, and actual entitlement footprint in an Install Base or CMDB system. No single system has enough context to safely answer: **Should we renew, discount, escalate, save, expand, or lock the proposal?**

This creates a practical operating problem:

| Business risk | What happens in the enterprise |
|---|---|
| Stale snapshot decisions | Teams price renewals from CRM or spreadsheet snapshots that miss live usage decline, escalations, fulfillment issues, or entitlement changes. |
| Vendor lock-in | AI workflows get hard-coded to one CRM or subscription platform, making stack changes expensive and risky. |
| Inconsistent decisions | Salesforce, Dynamics, Oracle, SAP, Zuora, NetSuite, Chargebee, and ServiceNow data shapes drive different logic unless they are normalized first. |
| Missing governance evidence | Revenue, finance, legal, and customer-success reviewers cannot always see why an AI recommendation was made. |
| Unsafe automation | If one source system is unavailable, an agent may either fail completely or proceed without making the missing context visible. |

The result is slower renewals, inconsistent discounting, weak auditability, and higher churn risk during the exact moment when commercial judgment matters most.

## How This App Solves It

This application demonstrates an enterprise-safe pattern for quote-to-cash agentic decision support:

| Solution capability | How the app implements it |
|---|---|
| Live commercial context | `ContextAssembler` gathers CRM, Oracle CPQ, Order Management Systems, Subscription, and Install Base data at decision time. |
| Vendor-independent integration | `MCPFactory` selects adapters from configuration, so changing Salesforce to Dynamics or Oracle FOM to SAP S/4HANA does not change agent code. |
| Canonical schema | Vendor payloads are normalized into frozen Pydantic models such as `UnifiedContext`, `CanonicalAccount`, `CanonicalSubscription`, and `CanonicalOrder`. |
| Resilient source handling | Context assembly uses `asyncio.gather(..., return_exceptions=True)` and returns complete, partial, or degraded context instead of crashing. |
| Deterministic decisioning | `DecisionAgent` calculates risk tier, recommended action, adjusted price, approval requirement, expansion offer, decision flag, and reasoning steps. |
| Full audit trail | The app persists context runs and agent decisions so every recommendation can be reviewed and explained. |
| Presentation-ready flow | The React UI walks stakeholders through the business problem, scenario selection, vendor stack, live context, decision cockpit, audit trail, and logical architecture. |

In short: the app does not try to make every enterprise system identical. It isolates vendor differences in MCP adapters, converts them into one commercial truth contract, and lets the decision agent operate on that contract with transparent governance.

## Executive Summary

Enterprise revenue teams rarely have one clean system of record. Customer health may live in CRM, quote logic in CPQ, fulfillment in Order Management Systems, renewal posture in a subscription platform, and entitlement reality in an install-base or CMDB system. If an AI agent prices renewals from stale snapshots or a single source, it can miss live churn signals, fulfillment risk, usage decline, escalations, or missing data.

This project demonstrates a production-shaped integration pattern:

- **Live context assembly** from selected enterprise systems at decision time.
- **MCP adapter isolation** for vendor-specific payloads, credentials, endpoints, and mock/real execution paths.
- **Frozen canonical schema** so agents reason over business objects instead of vendor APIs.
- **Deterministic decisioning** for risk tier, recommended action, adjusted price, approval posture, expansion offer, and decision flag.
- **Auditability by design**: assembled context, decision output, reasoning trace, source path, and conflict handling are persisted.
- **Demo mode with zero external credentials**, backed entirely by `seed_data/`.

## What This Proves

| Claim | Implementation proof |
|---|---|
| Vendor swaps do not require agent rewrites | `MCPFactory` selects adapters from runtime settings; `DecisionAgent` only consumes `UnifiedContext`. |
| Same underlying account facts produce the same business decision | CRM, Order Management Systems, Subscription, and Install Base adapters normalize into identical canonical objects. |
| Live context changes the decision | Scenario 1 compares stale snapshot posture with live MCP-assembled context. |
| Missing systems are governed, not hidden | Partial/degraded context sets completeness and decision flags for human review or proposal lock. |
| Every decision is explainable | Reasoning trace and stored audit evidence are available through API and UI. |

## Enterprise Capability Map

| Capability | Why it matters | Where it lives |
|---|---|---|
| Vendor abstraction | Keeps agent logic independent from Salesforce, Dynamics, Oracle, SAP, Zuora, NetSuite, Chargebee, or ServiceNow APIs. | `mcp/`, `MCPFactory`, adapter packages |
| Canonical commercial context | Gives the agent one stable business contract for account, opportunity, order, subscription, activity, and installed-product facts. | `context/models.py`, `context/normalizer.py` |
| Concurrent context assembly | Prevents one slow system from blocking all others and records partial-source evidence when a dependency fails. | `context/assembler.py` |
| Deterministic decision support | Makes renewal recommendations repeatable, testable, auditable, and suitable for governance review. | `agents/decision_agent.py` |
| Audit evidence | Captures context, decision, source stack, reasoning, and run history for traceability. | `audit/`, `/agent/runs`, `/audit/{context_run_id}` |
| Executive demo flow | Lets stakeholders understand the business problem, integration stack, live context, decision, and audit trail from the UI. | `ui/src/` |

## Application Flow

```text
Enterprise Systems
  CRM + CPQ + Order Management Systems + Subscription + Install Base
        |
        v
MCP Adapter Layer
  vendor-specific mock_call / real_call paths, auth, endpoints, readiness
        |
        v
ContextAssembler
  asyncio.gather(..., return_exceptions=True), never raises to caller
        |
        v
UnifiedContext
  frozen canonical Account, Opportunity, Orders, Subscription, Activities,
  Installed Products, source attribution, completeness, conflict resolution
        |
        v
DecisionAgent
  risk tier, action, adjusted price, approval posture, expansion offer,
  decision flag, reasoning trace
        |
        v
Audit Store + React Decision Support UI
```

The React app includes a dedicated **Logical Architecture** tab with an SVG diagram of this runtime flow.

## Vendor Support Matrix

| Domain slot | Adapter implementations | Canonical output |
|---|---|---|
| CRM | Salesforce CRM, Microsoft Dynamics 365, Oracle CX Sales | Account, Opportunity, Contact, Activity |
| CPQ | Oracle CPQ Cloud | Product, PriceBook, Quote/pricing context |
| Order Management Systems | Oracle FOM, Salesforce Order Management, SAP S/4HANA, Zuora Order Management, NetSuite Order Management | Order, OrderLine, FulfillmentStatus |
| Subscription | Oracle Subscription Cloud, Zuora Sub, Chargebee, Salesforce Revenue Cloud | Subscription, UsageHealth, RenewalSignal |
| Install Base | Oracle Install Base, Salesforce Asset Management, ServiceNow CMDB | InstalledProduct, Entitlement |

Current implementation: **16 adapters** across five commercial-system slots.

## Runtime Configuration

Demo mode runs end-to-end without credentials.

| Business slot | Setting | Values |
|---|---|---|
| Runtime mode | `APP_MODE` | `demo`, `real` |
| CRM system | `CRM_PROVIDER` | `salesforce`, `dynamics`, `oracle_crm` |
| Order Management Systems | `OMS_PROVIDER` | `oracle_fom`, `salesforce_oms`, `sap_s4hana`, `zuora_oms`, `netsuite` |
| Subscription platform | `SUB_PROVIDER` | `oracle_subscription`, `zuora_sub`, `chargebee`, `salesforce_revenue` |
| Install-base source | `INSTALL_BASE_PROVIDER` | `oracle_install_base`, `salesforce_asset`, `servicenow_cmdb` |
| Install-base enrichment | `INSTALL_BASE_ENABLED` | `true`, `false` |
| Pricing guardrail | `MIN_MARGIN_FLOOR` | default `0.18` |
| Approval guardrail | `APPROVAL_DISCOUNT_THRESHOLD` | default `0.10` |
| Audit persistence | `DATABASE_URL` | default `sqlite+aiosqlite:///./audit.db` |

The UI exposes vendor selection through the **Vendor Stack** page. Changing selections calls `/settings`, updates runtime adapter selection, and affects subsequent context assembly and decisions.

## Demo Scenarios

The scenario catalogue is designed to show different business branches, not seven copies of the same flow.

| # | Scenario | Account | Stack pattern | Expected branch |
|---|---|---|---|---|
| 1 | TechCorp Snapshot vs Live | `ACC-001` | Salesforce + Oracle FOM + Oracle Sub | Live high risk, risk-adjusted renewal at `$79,500` |
| 2 | GlobalBanking Happy Path | `ACC-002` | Salesforce + Oracle FOM + Oracle Sub | Low risk, standard renewal with expansion offer |
| 3 | CRM Vendor Swap | `ACC-002` | Dynamics + Oracle FOM + Oracle Sub | Same decision as Scenario 2 with zero agent changes |
| 4 | Non-Salesforce Stack | `ACC-003` | Oracle CRM + SAP Order Management Systems + Zuora Sub | Critical risk, escalate to CSM, proposal locked |
| 5 | Mixed Vendor Stack | `ACC-001` | Salesforce + Zuora Order Management Systems + Chargebee | High risk, risk-adjusted renewal through mixed stack |
| 6 | Degraded Context | `ACC-003` | Salesforce + Oracle FOM + simulated subscription timeout | Partial context, human review required |
| 7 | RetailCo Save Play | `ACC-004` | Salesforce + Oracle FOM + Oracle Sub | High risk, low upsell fit, save-play motion |

## Decision Semantics

`DecisionAgent` uses renewal signals assembled from canonical subscription, activity, order, product, and account data.

| Output | Meaning |
|---|---|
| `risk_tier` | `low`, `medium`, `high`, or `critical` risk derived from usage, escalations, urgency, and sentiment. |
| `recommended_action` | `standard_renewal`, `risk_adjusted_renewal`, `save_play`, or `escalate_to_csm`. |
| `adjusted_price` | Renewal price after deterministic risk multiplier and margin guardrail. |
| `approval_required` | True when discount exceeds threshold or margin guardrail intervenes. |
| `decision_flag` | Governance blocker: `none`, `requires_human_review`, or `proposal_locked`. UI renders `none` as **No blocking flag**. |
| `confidence` | Context completeness: `complete`, `partial`, or `degraded`. |

Important distinction: high risk does not automatically mean proposal lock. A high-risk account can still have `decision_flag = none` if context is complete and the recommendation can proceed without governance intervention.

## UI Experience

The React app is organized as an enterprise decision-support flow:

1. **Overview**: business problem and why live context matters.
2. **Demo Scenarios**: selectable scenario runbook with seven decision branches.
3. **Vendor Stack**: runtime vendor selection and adapter-slot matrix.
4. **Live Context**: assembled UnifiedContext with source stack, renewal posture, opportunity/order detail, install base, recent activity, and conflict handling.
5. **Decision Cockpit**: risk, price, action, approval posture, and reasoning trace.
6. **Audit Trail**: grouped decision history with stored evidence.
7. **Architecture**: adapter slots, canonical contract, and vendor-isolation explanation.
8. **Logical Architecture**: SVG diagram of the full runtime system.

## API Surface

| Endpoint | Purpose |
|---|---|
| `GET /settings` | Return current runtime settings. |
| `POST /settings` | Update vendor selection and runtime settings. |
| `GET /readiness` | Check all 16 adapter paths and return status/latency. |
| `POST /context/assemble` | Assemble and persist `UnifiedContext` for an account. |
| `GET /context/{context_run_id}` | Retrieve a stored context run. |
| `POST /context/compare` | Compare snapshot placeholder with live context. |
| `POST /agent/run` | Assemble context, run `DecisionAgent`, persist context and decision. |
| `GET /agent/runs` | List stored agent decisions. |
| `GET /audit/{context_run_id}` | Retrieve audit evidence for a context run. |
| `POST /demo/{scenario}` | Run demo scenario `1` through `7`. |

## Governance And Security Posture

This repository is intentionally structured so enterprise controls can be added at the boundaries where they belong:

- **Credentials** stay in environment configuration and are not required in `APP_MODE=demo`.
- **Vendor authentication** belongs inside each adapter `_real_call` path, not in agent logic.
- **Source evidence** travels with each assembled context so reviewers can see which systems contributed to a decision.
- **Decision flags** separate business risk from governance blockers such as missing context or locked proposals.
- **Audit storage** records repeatable decision evidence and can be replaced with a managed enterprise database by changing `DATABASE_URL`.
- **Deterministic rules** keep the reference implementation explainable before any organization adds probabilistic models or human approval workflows.

## Repository Structure

```text
api/                 FastAPI app, routers, runtime settings
agents/              RenewalSignalBuilder and deterministic DecisionAgent
audit/               SQLAlchemy async audit models and audit store
context/             Frozen canonical schema, assembler, normalizer, resolver, validator
demo/                Scenario runner for demo paths
mcp/                 Base MCP server, interfaces, factory, 16 adapter implementations
seed_data/           Demo fixtures for CRM, orders, subscription, activities, install base
tests/               Unit/API tests with 80% coverage gate
ui/                  React + Vite + TypeScript decision-support app
docs/                Tracked architecture and developer walkthrough docs
```

## Developer Documentation

| Document | Purpose |
|---|---|
| `docs/architecture.md` | Enterprise architecture reference for runtime components, adapter strategy, context assembly, decisioning, audit, UI, and productionization boundaries. |
| `docs/developer-flow-walkthrough.md` | Code-oriented walkthrough from UI action to FastAPI router, runtime settings, MCP adapters, context assembly, decision agent, audit persistence, and UI rendering. |

## Quick Start

Prerequisites:

- Python 3.12
- `uv`
- Node.js 18+ and npm
- Docker, only if using the container path

Install and verify backend:

```bash
make install
make seed
make test
make lint
```

Run the API:

```bash
make dev-api
```

Run the UI in another terminal:

```bash
cd ui
npm install
npm run dev -- --port 3001
```

Open:

```text
http://127.0.0.1:3001/
```

Run the default CLI demo:

```bash
make demo
```

Run all demo scenarios:

```bash
make demo-all
```

## Docker Path

Build and start the API container:

```bash
make docker-up
```

The Compose file runs the API in `APP_MODE=demo` and persists SQLite audit data in the `audit-data` volume.

## Validation Gates

The project is intentionally wired with production-style gates:

```bash
make lint
make test
cd ui && npm run build
```

Current expected test posture:

- Pytest passes.
- Coverage gate is enforced at `80%`.
- Ruff passes.
- Mypy strict passes for `context`, `agents`, `api`, and `mcp`.
- UI TypeScript build passes.

## Demo Data Model

`seed_data/` contains four canonical accounts plus vendor-shaped representations:

| Account | Business pattern |
|---|---|
| `ACC-001` TechCorp Inc | High risk, declining usage, expansion offer, snapshot-vs-live proof. |
| `ACC-002` GlobalBanking Corp | Healthy enterprise renewal with expansion eligibility. |
| `ACC-003` MidwestManufacturing | Critical risk, escalations, proposal lock path. |
| `ACC-004` RetailCo Stores | High risk with low expansion fit, save-play branch. |

Adapters load from these fixtures in demo mode. The same underlying account is represented in each vendor’s payload shape, then normalized back into the canonical schema.

## Real-Mode Integration Boundary

Every adapter includes:

- `_mock_call`: used by `APP_MODE=demo`, backed by `seed_data/`.
- `_real_call`: documented vendor API path or `NotImplementedError` stub with comments for real integration.

Real mode is intentionally not credentialed by default. To wire a live system, provide credentials in `.env`, complete the relevant `_real_call`, and keep the mapper output identical to the canonical contract.

## Productionization Checklist

Before promoting this pattern into an enterprise tenant, complete these items for each selected provider:

- Implement and test the adapter `_real_call` with the target vendor API, auth method, retry policy, timeout, and pagination behavior.
- Validate canonical mapping parity by comparing demo fixtures with live responses for the same account shape.
- Move audit persistence from local SQLite to the organization’s managed database.
- Add tenant-specific secret management, request tracing, and operational telemetry.
- Add role-based UI and API access for revenue operations, architecture reviewers, and audit reviewers.
- Extend decision policies only inside the agent/rules layer, keeping vendor-specific behavior inside adapters.

## Engineering Principles

- **Adapter isolation**: no agent imports vendor-specific adapters or payloads.
- **Canonical-first decisions**: all decision logic consumes frozen Pydantic v2 models.
- **Concurrent assembly**: `ContextAssembler` uses `asyncio.gather(..., return_exceptions=True)`.
- **Graceful degradation**: assembly never raises to the caller; it returns `UnifiedContext` with completeness and missing-source evidence.
- **Auditable execution**: context and decision records are stored for traceability.
- **Config-driven vendor selection**: UI and API can switch vendors without agent-code changes.

## Useful Commands

```bash
make install        # uv sync with Python 3.12 and dev dependencies
make seed           # initialize seed/audit data path
make dev-api        # FastAPI on http://127.0.0.1:8000
make dev-ui         # Vite default dev server from ui/
make demo           # run scenario 1
make demo-all       # run scenarios 1-7
make test           # pytest with coverage gate
make lint           # ruff + mypy strict
make docker-up      # build and start API container
make clean          # remove local caches and audit db
```

## Suggested Demo Talk Track

1. Start with **Overview** to frame stale snapshots vs live commercial context.
2. Open **Demo Scenarios** and run Scenario 1 to show snapshot-vs-live risk change.
3. Run Scenario 3 to prove CRM vendor swap without agent code changes.
4. Open **Vendor Stack** and switch Order Management Systems, Subscription, or Install Base providers.
5. Open **Live Context** to show the exact source stack and unified business facts.
6. Open **Decision Cockpit** to show risk, price, action, approval posture, and reasoning.
7. Open **Audit Trail** to show stored evidence and grouped equivalent decisions.
8. Close with **Logical Architecture** to explain the full enterprise pattern.

## Status

This repository is a production-grade reference implementation for the integration and decisioning pattern. Demo mode is complete and credential-free. Real-mode connectors are intentionally bounded behind documented adapter stubs so each enterprise integration can be completed with the proper tenant, authentication, and governance controls.
