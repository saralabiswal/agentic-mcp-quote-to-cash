# Architecture — agentic-mcp-crm-integration

## Purpose

MCP-powered enterprise integration layer that assembles live, unified commercial
context from any CRM + any Order Management + any Subscription system, with Oracle
CPQ Cloud always as the pricing and quoting layer. AI agents make decisions on real
data — not stale batch snapshots — regardless of which vendor combination the
customer runs.

The headline claim: **"Vendor Adapters — plug in any combination."**

14 adapters. 4 abstract interfaces. 1 canonical schema. Zero agent code changes
when you swap vendors.

---

## Vendor Support Matrix

### CRM — ONE of these (config-driven)

| Adapter | Vendor | Mock | Real |
|---|---|---|---|
| `salesforce_mcp.py` | Salesforce CRM | ✅ Full | ✅ REST API v57+ OAuth2 |
| `dynamics_mcp.py` | MS Dynamics 365 | ✅ Full | ✅ Dataverse API + Azure AD |
| `oracle_crm_mcp.py` | Oracle CX Sales | ✅ Full | ✅ OCI REST + API key |

### CPQ — ALWAYS Oracle

| Adapter | Vendor | Mock | Real |
|---|---|---|---|
| `oracle_cpq_mcp.py` | Oracle CPQ Cloud | ✅ Full | ✅ Oracle CPQ REST API |

### Order Management — ONE of these (config-driven)

| Adapter | Vendor | Mock | Real |
|---|---|---|---|
| `oracle_fom_mcp.py` | Oracle Fusion FOM | ✅ Full | ✅ OIC endpoints |
| `salesforce_oms_mcp.py` | Salesforce Order Management | ✅ Full | Documented stub |
| `sap_oms_mcp.py` | SAP S/4HANA OMS | ✅ Full | Documented stub |
| `zuora_oms_mcp.py` | Zuora (order component) | ✅ Full | Documented stub |
| `netsuite_oms_mcp.py` | Oracle NetSuite OMS | ✅ Full | Documented stub |

### Subscription Management — ONE of these (config-driven)

| Adapter | Vendor | Mock | Real |
|---|---|---|---|
| `oracle_sub_mcp.py` | Oracle Fusion Subscription Cloud | ✅ Full | ✅ OIC endpoints |
| `zuora_sub_mcp.py` | Zuora Subscription Management | ✅ Full | Documented stub |
| `chargebee_sub_mcp.py` | Chargebee | ✅ Full | Documented stub |
| `salesforce_rev_mcp.py` | Salesforce Revenue Cloud | ✅ Full | Documented stub |

### Install Base — Oracle only (optional enrichment)

| Adapter | Vendor | Mock | Real |
|---|---|---|---|
| `oracle_install_base_mcp.py` | Oracle Install Base | ✅ Full | Documented stub |

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| API | FastAPI 0.111, Pydantic v2 | Async throughout |
| MCP | Python MCP SDK (mcp>=1.0) | One server class per adapter |
| Context | asyncio.gather() | Concurrent pull from all active sources |
| Storage | SQLite (local), PostgreSQL (prod path) | SQLAlchemy 2.0 async |
| Frontend | React 18 + Vite + TypeScript | Tailwind CSS |
| Testing | pytest, pytest-asyncio | 80% coverage gate |
| CI | GitHub Actions | ruff + mypy + pytest |
| Packaging | pyproject.toml, uv | |
| Container | Docker + docker-compose | |
| Languages | Python 3.12, TypeScript 5 | |

---

## Repository Structure

```
agentic-mcp-crm-integration/
│
├── api/
│   ├── main.py                              # FastAPI app, lifespan, CORS, router wiring
│   ├── dependencies.py                      # Settings, DB session, assembler singletons
│   └── routers/
│       ├── context.py                       # POST /context/assemble, GET /context/{id},
│       │                                    # POST /context/compare
│       ├── agent.py                         # POST /agent/run, GET /agent/runs
│       ├── audit.py                         # GET /audit/{context_run_id}
│       ├── demo.py                          # POST /demo/{scenario}
│       └── settings.py                      # GET/POST /settings, GET /readiness
│
├── mcp/
│   ├── base.py                              # BaseMCPServer: auth, timeout, mock/real routing
│   ├── factory.py                           # MCPFactory: returns correct adapter from config
│   ├── interfaces/
│   │   ├── crm_interface.py                 # AbstractCRMServer
│   │   ├── cpq_interface.py                 # AbstractCPQServer
│   │   ├── oms_interface.py                 # AbstractOMSServer
│   │   └── sub_interface.py                 # AbstractSubServer
│   └── adapters/
│       ├── crm/
│       │   ├── salesforce/
│       │   │   ├── salesforce_mcp.py        # FULL — mock + real (Salesforce REST API)
│       │   │   └── salesforce_mapper.py     # SF schema → canonical
│       │   ├── dynamics/
│       │   │   ├── dynamics_mcp.py          # FULL — mock + real (Dataverse API)
│       │   │   └── dynamics_mapper.py       # Dynamics schema → canonical
│       │   └── oracle_crm/
│       │       ├── oracle_crm_mcp.py        # FULL — mock + real (OCI REST)
│       │       └── oracle_crm_mapper.py     # Oracle CX schema → canonical
│       ├── cpq/
│       │   └── oracle_cpq/
│       │       ├── oracle_cpq_mcp.py        # FULL — mock + real (Oracle CPQ REST)
│       │       └── oracle_cpq_mapper.py     # CPQ schema → CanonicalProduct/Quote
│       ├── oms/
│       │   ├── oracle_fom/
│       │   │   ├── oracle_fom_mcp.py        # FULL — mock + real (OIC)
│       │   │   └── oracle_fom_mapper.py
│       │   ├── salesforce_oms/
│       │   │   ├── salesforce_oms_mcp.py    # FULL mock — real stub documented
│       │   │   └── salesforce_oms_mapper.py
│       │   ├── sap_oms/
│       │   │   ├── sap_oms_mcp.py           # FULL mock — real stub documented
│       │   │   └── sap_oms_mapper.py
│       │   ├── zuora_oms/
│       │   │   ├── zuora_oms_mcp.py         # FULL mock — real stub documented
│       │   │   └── zuora_oms_mapper.py
│       │   └── netsuite_oms/
│       │       ├── netsuite_oms_mcp.py      # FULL mock — real stub documented
│       │       └── netsuite_oms_mapper.py
│       ├── sub/
│       │   ├── oracle_sub/
│       │   │   ├── oracle_sub_mcp.py        # FULL — mock + real (OIC)
│       │   │   └── oracle_sub_mapper.py
│       │   ├── zuora_sub/
│       │   │   ├── zuora_sub_mcp.py         # FULL mock — real stub documented
│       │   │   └── zuora_sub_mapper.py
│       │   ├── chargebee/
│       │   │   ├── chargebee_mcp.py         # FULL mock — real stub documented
│       │   │   └── chargebee_mapper.py
│       │   └── salesforce_revenue/
│       │       ├── salesforce_rev_mcp.py    # FULL mock — real stub documented
│       │       └── salesforce_rev_mapper.py
│       └── install_base/
│           ├── oracle_install_base_mcp.py   # FULL mock — real stub documented
│           └── oracle_install_base_mapper.py
│
├── context/
│   ├── models.py                            # All 10 canonical Pydantic objects
│   ├── assembler.py                         # ContextAssembler: concurrent pull
│   ├── normalizer.py                        # Maps any adapter response → canonical
│   ├── conflict_resolver.py                 # Field-level conflict rules
│   └── validator.py                         # Completeness check
│
├── agents/
│   ├── decision_agent.py                    # DecisionAgent: renewal risk + pricing
│   └── renewal_signal_builder.py            # Builds RenewalSignal from context
│
├── audit/
│   ├── models.py                            # SQLAlchemy ORM tables
│   └── audit_store.py                       # Persist + query context/agent runs
│
├── demo/
│   ├── runner.py                            # DemoRunner
│   ├── scenario_1_snapshot_vs_live.py       # Stale vs live — different decisions
│   ├── scenario_2_sf_to_oracle.py           # Salesforce + Oracle FOM + Oracle Sub
│   ├── scenario_3_dynamics_to_oracle.py     # Dynamics + Oracle FOM + Oracle Sub
│   ├── scenario_4_sap_zuora.py             # Oracle CRM + SAP OMS + Zuora Sub
│   ├── scenario_5_full_stack_variation.py   # Salesforce + Zuora OMS + Chargebee
│   └── scenario_6_degraded.py              # Sub system timeout → partial context
│
├── seed_data/
│   ├── accounts.json                        # 3 accounts: ACC-001, ACC-002, ACC-003
│   ├── opportunities.json
│   ├── contacts.json
│   ├── subscriptions.json
│   ├── orders.json
│   ├── activities.json
│   └── install_base.json
│
├── ui/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/client.ts
│       └── pages/
│           ├── About.tsx                    # Business problem — WHY this exists
│           ├── StackConfigurator.tsx        # All 14 adapters, pick your combination
│           ├── ContextExplorer.tsx          # Live context assembly view
│           ├── SnapshotDemo.tsx             # Stale vs live comparison
│           ├── AgentRuns.tsx                # Decision history + audit trail
│           └── Architecture.tsx            # System diagram + active adapters
│
├── tests/
│   ├── conftest.py
│   ├── test_crm_adapters.py                # All 3 CRM adapters
│   ├── test_cpq_adapter.py
│   ├── test_oms_adapters.py                # All 5 OMS adapters
│   ├── test_sub_adapters.py                # All 4 Sub adapters
│   ├── test_install_base_adapter.py
│   ├── test_context_assembly.py
│   ├── test_conflict_resolver.py
│   ├── test_decision_agent.py
│   └── test_api.py
│
├── docs/
│   └── architecture.md
│
├── .env.example
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Architecture Layers

### Layer 1 — MCP Adapter Layer

#### Abstract Interfaces

```python
# crm_interface.py
class AbstractCRMServer(BaseMCPServer):
    async def get_account(self, crm_account_id: str) -> dict: ...
    async def get_opportunities(self, crm_account_id: str) -> list[dict]: ...
    async def get_contacts(self, crm_account_id: str) -> list[dict]: ...
    async def get_activities(self, crm_account_id: str, days: int = 90) -> list[dict]: ...

# cpq_interface.py
class AbstractCPQServer(BaseMCPServer):
    async def get_product_catalog(self, segment: str) -> list[dict]: ...
    async def get_pricing_context(self, account_id: str, products: list[str]) -> dict: ...
    async def create_quote_draft(self, context: dict) -> dict: ...

# oms_interface.py
class AbstractOMSServer(BaseMCPServer):
    async def get_orders(self, account_id: str, months: int = 24) -> list[dict]: ...

# sub_interface.py
class AbstractSubServer(BaseMCPServer):
    async def get_subscription(self, account_id: str) -> dict: ...
    async def get_renewal_signals(self, subscription_id: str) -> dict: ...
```

#### MCPFactory

Reads provider settings and returns correct adapter. Nothing above the factory
imports adapters directly.

```python
class MCPFactory:
    def get_crm_server(self) -> AbstractCRMServer:
        return {
            CRMProvider.SALESFORCE:   SalesforceMCP,
            CRMProvider.DYNAMICS:     DynamicsMCP,
            CRMProvider.ORACLE_CRM:   OracleCRMMCP,
        }[self.settings.crm_provider](self.settings)

    def get_cpq_server(self) -> AbstractCPQServer:
        return OracleCPQMCP(self.settings)   # always Oracle

    def get_oms_server(self) -> AbstractOMSServer:
        return {
            OMSProvider.ORACLE_FOM:        OracleFOMMCP,
            OMSProvider.SALESFORCE_OMS:    SalesforceOMSMCP,
            OMSProvider.SAP_S4HANA:        SAPOMSMCP,
            OMSProvider.ZUORA_OMS:         ZuoraOMSMCP,
            OMSProvider.NETSUITE:          NetsuiteOMSMCP,
        }[self.settings.oms_provider](self.settings)

    def get_sub_server(self) -> AbstractSubServer:
        return {
            SubProvider.ORACLE_SUBSCRIPTION: OracleSubMCP,
            SubProvider.ZUORA_SUB:           ZuoraSubMCP,
            SubProvider.CHARGEBEE:           ChargebeeMCP,
            SubProvider.SALESFORCE_REVENUE:  SalesforceRevenueMCP,
        }[self.settings.sub_provider](self.settings)

    def get_install_base_server(self) -> OracleInstallBaseMCP:
        return OracleInstallBaseMCP(self.settings)
```

#### BaseMCPServer

```python
class BaseMCPServer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.mode = settings.app_mode
        self.timeout = settings.mcp_timeout_seconds

    async def _call_tool(self, tool_name: str, params: dict) -> dict:
        if self.mode == AppMode.DEMO:
            return await asyncio.wait_for(
                self._mock_call(tool_name, params),
                timeout=self.timeout
            )
        return await asyncio.wait_for(
            self._real_call(tool_name, params),
            timeout=self.timeout
        )

    async def _mock_call(self, tool_name: str, params: dict) -> dict:
        raise NotImplementedError

    async def _real_call(self, tool_name: str, params: dict) -> dict:
        raise NotImplementedError
```

#### Adapter Specifications — All 14

**CRM Adapters — all implement AbstractCRMServer + mapper**

`salesforce_mcp.py`:
- Mock: loads from seed_data/ by account_id
- Real: `GET /services/data/v57.0/sobjects/Account/{id}`,
  `GET /services/data/v57.0/query/?q=SELECT+...+FROM+Opportunity+WHERE+AccountId='{id}'`
- Auth: OAuth2 client_credentials, Bearer token in header

`dynamics_mcp.py`:
- Mock: same seed accounts, Dynamics field naming convention
- Real: `GET https://{org}.api.crm.dynamics.com/api/data/v9.2/accounts({guid})`,
  `GET /api/data/v9.2/opportunities?$filter=_accountid_value eq {guid}`
- Auth: Azure AD app registration, MSAL token

`oracle_crm_mcp.py`:
- Mock: same seed accounts, Oracle CX Sales field naming
- Real: `GET /crmRestApi/resources/latest/accounts/{id}`,
  `GET /crmRestApi/resources/latest/opportunities?q=AccountId={id}`
- Auth: OCI API key or Basic auth

**CPQ Adapter**

`oracle_cpq_mcp.py`:
- Mock: product catalog with 8 products, pricing tiers for enterprise/mid_market/smb
- Real: `GET /rest/v1/products`, `POST /rest/v1/quotes`
- Auth: Oracle CPQ API key

**OMS Adapters — all implement AbstractOMSServer + mapper**

`oracle_fom_mcp.py`:
- Mock: 2-3 historical orders per seed account
- Real: OIC REST endpoint `GET /ic/api/integration/v1/flows/.../order/{account_id}`

`salesforce_oms_mcp.py`:
- Mock: 2-3 orders per seed account in Salesforce Order schema
- Real: `GET /services/data/v57.0/query/?q=SELECT+...+FROM+Order+WHERE+AccountId='{id}'`
- Note: Salesforce OMS uses Salesforce REST, same auth as CRM

`sap_oms_mcp.py`:
- Mock: 2-3 orders per seed account in SAP schema
- Real: `GET https://{host}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder?$filter=SoldToParty eq '{id}'`
- Auth: SAP Basic auth or OAuth2

`zuora_oms_mcp.py`:
- Mock: 2-3 orders per seed account in Zuora schema
- Real: `GET https://rest.zuora.com/v1/orders?accountKey={account_key}`
- Auth: Zuora Bearer token (client_credentials)

`netsuite_oms_mcp.py`:
- Mock: 2-3 orders per seed account in NetSuite schema
- Real: NetSuite REST `GET /services/rest/record/v1/salesorder?q=entity IS {id}`
- Auth: NetSuite OAuth1 (TBA)

**Sub Adapters — all implement AbstractSubServer + mapper**

`oracle_sub_mcp.py`:
- Mock: subscription record with usage signals for each seed account
- Real: OIC endpoint for Oracle Subscription Cloud

`zuora_sub_mcp.py`:
- Mock: Zuora subscription schema with usage metrics
- Real: `GET https://rest.zuora.com/v1/subscriptions/accounts/{account_key}`

`chargebee_mcp.py`:
- Mock: Chargebee subscription schema
- Real: `GET https://{site}.chargebee.com/api/v2/subscriptions?customer_id[is]={id}`
- Auth: Chargebee API key as Basic auth password

`salesforce_rev_mcp.py`:
- Mock: Salesforce Revenue Cloud subscription schema
- Real: Salesforce CPQ API `GET /services/data/v57.0/query?q=SELECT+...+FROM+SBQQ__Subscription__c`

**Install Base Adapter**

`oracle_install_base_mcp.py`:
- Mock: installed products per seed account (product_id, quantity, install_date, location)
- Real: Oracle Install Base REST API
- Used to enrich CanonicalAccount.installed_base

---

### Layer 2 — Context Assembly Layer

**ContextAssembler flow:**

```python
async def assemble(self, account_id: str) -> UnifiedContext:
    # Concurrent pull from all 5 sources (CRM + CPQ + OMS + Sub + InstallBase)
    crm_result, cpq_result, oms_result, sub_result, ib_result = await asyncio.gather(
        self._pull_crm(account_id),
        self._pull_cpq(account_id),
        self._pull_oms(account_id),
        self._pull_sub(account_id),
        self._pull_install_base(account_id),
        return_exceptions=True
    )
    # Handle exceptions per source → missing_sources
    # Normalize each successful result
    # Run ConflictResolver
    # Run RenewalSignalBuilder
    # Run ContextValidator
    # Return UnifiedContext
```

**ConflictResolver rules:**
```
account_value:     HIGHER value wins
close_date:        subscription_system wins (authoritative)
renewal_date:      subscription_system wins (authoritative)
industry:          MORE_SPECIFIC wins
account_name:      CRM wins (master of record)
opportunity_stage: MOST_ADVANCED wins
```

**ContextValidator completeness:**
```
COMPLETE:  all 5 sources responded
PARTIAL:   1-2 sources timed out (non-critical)
DEGRADED:  3+ sources timed out OR subscription source failed
```

---

### Layer 3 — Decision Agent

DecisionAgent consumes UnifiedContext. Deterministic. No LLM in core path.

**Risk tiers:**
```
risk_score >= 0.75 → CRITICAL → escalate_to_csm
risk_score >= 0.50 → HIGH     → risk_adjusted_renewal (12% off)
risk_score >= 0.25 → MEDIUM   → risk_adjusted_renewal (7% off)
else               → LOW      → standard_renewal + expansion_offer if propensity > 0.65
```

**Guardrails (hard, never bypassed):**
- Adjusted price never below min_margin_floor
- Discount > threshold always sets approval_required=True
- DEGRADED context always sets proposal_locked=True
- escalate_to_csm always sets proposal_locked=True

---

### Layer 4 — Audit Store

4 tables indexed by context_run_id:
- `context_runs` — assembly metadata
- `conflict_records` — per-field conflict resolutions
- `agent_runs` — decisions with reasoning steps
- `source_calls` — per-MCP call timing and success

---

## Canonical Schema — 10 Objects

All defined in `context/models.py`. All frozen Pydantic v2 models.

```python
# Enums
class CRMProvider(str, Enum):
    SALESFORCE = "salesforce"
    DYNAMICS = "dynamics"
    ORACLE_CRM = "oracle_crm"

class OMSProvider(str, Enum):
    ORACLE_FOM = "oracle_fom"
    SALESFORCE_OMS = "salesforce_oms"
    SAP_S4HANA = "sap_s4hana"
    ZUORA_OMS = "zuora_oms"
    NETSUITE = "netsuite"

class SubProvider(str, Enum):
    ORACLE_SUBSCRIPTION = "oracle_subscription"
    ZUORA_SUB = "zuora_sub"
    CHARGEBEE = "chargebee"
    SALESFORCE_REVENUE = "salesforce_revenue"

class OMSProvider(str, Enum): ...   # as above
class AppMode(str, Enum): DEMO="demo"; REAL="real"
class Segment(str, Enum): ENTERPRISE="enterprise"; MID_MARKET="mid_market"; SMB="smb"
class OpportunityType(str, Enum): ...
class OpportunityStage(str, Enum): ...
class ContactRole(str, Enum): ...
class SubscriptionStatus(str, Enum): ...
class UrgencyTier(str, Enum): CRITICAL="critical"; URGENT="urgent"; NORMAL="normal"; EARLY="early"
class BillingFrequency(str, Enum): ...
class UsageTrend(str, Enum): GROWING="growing"; STABLE="stable"; DECLINING="declining"; CRITICAL="critical"
class OrderType(str, Enum): ...
class OrderStatus(str, Enum): ...
class QuoteStatus(str, Enum): ...
class ActivityType(str, Enum): ...
class Sentiment(str, Enum): ...
class RiskTier(str, Enum): ...
class RecommendedAction(str, Enum): ...
class Completeness(str, Enum): COMPLETE="complete"; PARTIAL="partial"; DEGRADED="degraded"
```

**Object 1 — CanonicalAccount**
```python
class CanonicalAccount(BaseModel):
    model_config = ConfigDict(frozen=True)
    canonical_account_id: str           # ACC-{hash}
    crm_source: CRMProvider
    crm_source_id: str
    name: str
    industry: str
    segment: Segment
    account_value: Decimal
    employee_count: int | None
    region: str
    health_score: float                 # 0.0–1.0
    last_activity_date: datetime | None
    owner_name: str | None
    installed_base: list[InstalledProduct] | None  # from install base adapter
```

**Objects 2–10:** CanonicalOpportunity, CanonicalContact, CanonicalSubscription,
CanonicalOrder + OrderLineItem, CanonicalQuote + QuoteLineItem, CanonicalProduct
+ PricingTier + ConfigRule, CanonicalActivity, RenewalSignal + ChurnIndicator
+ PricingRecommendation, UnifiedContext + SourceAttribution + ConflictResolution

**UnifiedContext (envelope):**
```python
class UnifiedContext(BaseModel):
    model_config = ConfigDict(frozen=True)
    context_run_id: str                 # CTX-{uuid4}
    assembled_at: datetime
    crm_provider: CRMProvider
    oms_provider: OMSProvider
    sub_provider: SubProvider
    account: CanonicalAccount
    opportunity: CanonicalOpportunity | None
    contacts: list[CanonicalContact]
    subscription: CanonicalSubscription | None
    orders: list[CanonicalOrder]
    activities: list[CanonicalActivity]
    renewal_signal: RenewalSignal | None
    source_attribution: dict[str, SourceAttribution]
    conflict_resolutions: list[ConflictResolution]
    context_completeness: Completeness
    missing_sources: list[str]
```

---

## Configuration

```python
class Settings(BaseSettings):
    # Stack selection — ALL 14 adapters selectable
    crm_provider: CRMProvider = CRMProvider.SALESFORCE
    oms_provider: OMSProvider = OMSProvider.ORACLE_FOM
    sub_provider: SubProvider = SubProvider.ORACLE_SUBSCRIPTION
    install_base_enabled: bool = True

    # App mode
    app_mode: AppMode = AppMode.DEMO

    # Timeouts
    mcp_timeout_seconds: int = 5
    context_assembly_timeout_seconds: int = 10

    # Database
    database_url: str = "sqlite+aiosqlite:///./audit.db"

    # Salesforce credentials (real mode)
    sf_instance_url: str = ""
    sf_client_id: str = ""
    sf_client_secret: str = ""

    # MS Dynamics credentials (real mode)
    dynamics_tenant_id: str = ""
    dynamics_client_id: str = ""
    dynamics_client_secret: str = ""
    dynamics_org_url: str = ""

    # Oracle credentials (real mode)
    oracle_crm_base_url: str = ""
    oracle_cpq_base_url: str = ""
    oracle_cpq_api_key: str = ""
    oracle_fom_oic_url: str = ""
    oracle_sub_oic_url: str = ""
    oracle_ib_api_key: str = ""

    # Non-Oracle OMS credentials (real mode)
    salesforce_oms_instance_url: str = ""  # reuses SF auth if SF CRM
    sap_host: str = ""
    sap_client: str = ""
    sap_username: str = ""
    sap_password: str = ""
    zuora_client_id: str = ""
    zuora_client_secret: str = ""
    netsuite_account_id: str = ""
    netsuite_consumer_key: str = ""

    # Non-Oracle Sub credentials (real mode)
    chargebee_site: str = ""
    chargebee_api_key: str = ""
    salesforce_revenue_instance_url: str = ""
```

---

## Demo Scenarios — 6 Scenarios

### Scenario 1 — Snapshot vs Live
- Account: ACC-001 (TechCorp Inc), CRM=salesforce
- Shows stale vs live decision difference
- Risk HIGH in live, MEDIUM in snapshot

### Scenario 2 — Salesforce + Oracle FOM + Oracle Sub
- Account: ACC-002 (GlobalBanking Corp)
- Full Oracle back-office + Salesforce CRM happy path

### Scenario 3 — Dynamics + Oracle FOM + Oracle Sub
- Same account as Scenario 2, same expected output
- Proves vendor-agnostic: zero agent code change

### Scenario 4 — Oracle CRM + SAP OMS + Zuora Sub
- Account: ACC-003 (MidwestManufacturing)
- Full non-Salesforce stack
- Shows SAP and Zuora adapters working

### Scenario 5 — Salesforce + Zuora OMS + Chargebee
- Account: ACC-001 (TechCorp Inc)
- Mixed vendor combination
- Shows Chargebee subscription signals

### Scenario 6 — Degraded Context
- Account: ACC-003, CRM=salesforce
- Simulate subscription adapter timeout
- context_completeness=PARTIAL, REQUIRES_HUMAN_REVIEW

---

## Seed Data — 3 Enterprise Accounts

All 14 adapters serve the SAME 3 accounts, each formatted per vendor schema.
The normalizer produces identical canonical output regardless of source adapter.

### ACC-001: TechCorp Inc
- Segment: enterprise, ARR $84K, renewal T+45
- usage_health: 0.41 declining, escalation_count_90d: 2
- Expected decision: HIGH risk, risk_adjusted_renewal, $79,500

### ACC-002: GlobalBanking Corp
- Segment: enterprise, ARR $245K, renewal T+67
- usage_health: 0.83 stable, escalation_count_90d: 0
- Expected decision: LOW risk, standard_renewal + expansion_offer

### ACC-003: MidwestManufacturing
- Segment: mid_market, ARR $38.5K, renewal T+22
- usage_health: 0.29 critical, escalation_count_90d: 4
- Expected decision: CRITICAL risk, escalate_to_csm

---

## UI Pages — 6 Pages

### About.tsx
Business problem — why this exists. Content from About_BusinessProblem.html.
5 sections: Problem / Why It's Hard / The Solution / What It Solves / Production Proof.

### StackConfigurator.tsx
All 14 adapters visible. User selects:
- CRM: Salesforce | MS Dynamics 365 | Oracle CX Sales
- CPQ: Oracle CPQ Cloud (fixed, not selectable)
- OMS: Oracle FOM | Salesforce OMS | SAP S/4HANA | Zuora | NetSuite
- Sub: Oracle Sub Cloud | Zuora | Chargebee | Salesforce Revenue Cloud
- Install Base: enable/disable toggle

Live preview: shows active adapter filenames + real API endpoint for each.
Calls POST /settings on change. Shows readiness status per source.
"This is the vendor-agnostic pattern in action" framing.

### ContextExplorer.tsx
Account dropdown → Assemble → show UnifiedContext with source attribution.

### SnapshotDemo.tsx
Side-by-side stale vs live. Highlight differing fields.

### AgentRuns.tsx
Decision history + full audit trail expandable per run.

### Architecture.tsx
Static system diagram showing all 4 layers and all 14 adapter slots.
Highlights currently active adapters in green.

---

## API Endpoints

```
POST /context/assemble          → UnifiedContext
GET  /context/{context_run_id}  → UnifiedContext (from audit)
POST /context/compare           → { snapshot, live }
POST /agent/run                 → AgentDecision (+ SSE stream)
GET  /agent/runs                → list[AgentRunSummary]
GET  /audit/{context_run_id}    → full audit record
POST /demo/{scenario}           → DemoResult (scenarios: 1-6)
GET  /settings                  → current stack config
POST /settings                  → update stack config (hot-swap)
GET  /readiness                 → per-source connectivity status for all 14
```

---

## CI Pipeline

```yaml
steps:
  - ruff check .
  - mypy --strict context/ agents/ api/ mcp/
  - pytest --cov=. --cov-fail-under=80 -q
  - docker build .
```

---

## Makefile Targets

```makefile
install      # pip install -e ".[dev]"
seed         # python -m seed_data.seeder
dev-api      # uvicorn api.main:app --reload --port 8000
dev-ui       # cd ui && npm run dev
demo         # python -m demo.runner 1      (snapshot vs live)
demo-all     # run all 6 demo scenarios
test         # pytest -q --cov
lint         # ruff check . && mypy ...
docker-up    # docker compose up --build
clean        # remove __pycache__, .pytest_cache, audit.db
```
