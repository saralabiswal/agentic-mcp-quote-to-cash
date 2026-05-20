# Tasks — agentic-mcp-crm-integration

Work through phases in order. Each phase has an acceptance criterion.
Do not start Phase N+1 until all tasks in Phase N pass tests and lint.

---

## Phase 0 — Project Scaffold

- [x] **T0.1** Create pyproject.toml
  - Python 3.12, dependencies: fastapi, uvicorn[standard], pydantic>=2.0,
    pydantic-settings, sqlalchemy>=2.0, aiosqlite, mcp>=1.0, httpx, python-dotenv
  - Dev: pytest, pytest-asyncio, pytest-cov, ruff, mypy, faker, httpx

- [x] **T0.2** Create full folder structure per ARCHITECTURE.md with __init__.py files

- [x] **T0.3** Create .env.example with all 30+ settings keys and inline comments

- [x] **T0.4** Create Makefile with all targets from ARCHITECTURE.md

- [x] **T0.5** Create .github/workflows/ci.yml — ruff + mypy + pytest --cov-fail-under=80

- [x] **T0.6** Create Dockerfile + docker-compose.yml — API on port 8000, SQLite volume

**Acceptance:** make install succeeds, make lint passes on empty stubs, make docker-up starts.

---

## Phase 1 — Canonical Schema

- [x] **T1.1** Define ALL enums in context/models.py
  - CRMProvider: salesforce | dynamics | oracle_crm
  - OMSProvider: oracle_fom | salesforce_oms | sap_s4hana | zuora_oms | netsuite
  - SubProvider: oracle_subscription | zuora_sub | chargebee | salesforce_revenue
  - AppMode, Segment, OpportunityType, OpportunityStage, ContactRole
  - SubscriptionStatus, UrgencyTier, BillingFrequency, UsageTrend
  - OrderType, OrderStatus, QuoteStatus, ActivityType, Sentiment
  - RiskTier, RecommendedAction, Completeness

- [x] **T1.2** Define InstalledProduct model
  ```python
  class InstalledProduct(BaseModel):
      product_id: str
      product_name: str
      quantity: int
      install_date: date
      location: str | None
      support_level: str | None
      end_of_support_date: date | None
  ```

- [x] **T1.3** Define all 10 canonical objects — all frozen Pydantic v2
  - CanonicalAccount (include installed_base: list[InstalledProduct] | None)
  - CanonicalOpportunity
  - CanonicalContact
  - CanonicalSubscription (computed: days_to_renewal, urgency_tier)
  - OrderLineItem + CanonicalOrder
  - QuoteLineItem + CanonicalQuote
  - PricingTier + ConfigRule + CanonicalProduct
  - CanonicalActivity
  - ChurnIndicator + PricingRecommendation + RenewalSignal
  - SourceAttribution + ConflictResolution + UnifiedContext

- [x] **T1.4** Tests (tests/test_models.py)
  - All 10 objects instantiate with valid data
  - Enum validation raises on invalid values
  - CanonicalSubscription computed fields correct
  - UnifiedContext serializes/deserializes cleanly

**Acceptance:** pytest tests/test_models.py passes, mypy passes on context/models.py

---

## Phase 2 — Settings + Config

- [x] **T2.1** Implement Settings (pydantic-settings) in api/dependencies.py
  - All fields from ARCHITECTURE.md configuration section
  - Singleton via @lru_cache
  - Mutable runtime override: RuntimeSettings wrapper that allows hot-swap

- [x] **T2.2** Tests: defaults, env override, all provider enums accepted

**Acceptance:** pytest tests/test_settings.py passes

---

## Phase 3 — MCP Base + Interfaces

- [x] **T3.1** Implement BaseMCPServer in mcp/base.py
  - mode-based routing (demo → _mock_call, real → _real_call)
  - Per-call timeout via asyncio.wait_for
  - MCPTimeoutError, MCPConnectionError custom exceptions

- [x] **T3.2** Implement 4 abstract interfaces in mcp/interfaces/
  - AbstractCRMServer: get_account, get_opportunities, get_contacts, get_activities
  - AbstractCPQServer: get_product_catalog, get_pricing_context, create_quote_draft
  - AbstractOMSServer: get_orders
  - AbstractSubServer: get_subscription, get_renewal_signals

- [x] **T3.3** Tests: base timeout, mode routing, abstract enforcement

**Acceptance:** pytest tests/test_mcp_base.py passes

---

## Phase 4 — All 14 MCP Adapters

### 4A — CRM Adapters

- [x] **T4A.1 — SalesforceMCP (FULL)**
File: mcp/adapters/crm/salesforce/salesforce_mcp.py
- Mock: loads seed_data/accounts.json, opportunities.json, contacts.json, activities.json
  filtered by account_id for each tool call
- Real: Salesforce REST API v57+
  - get_account: GET /services/data/v57.0/sobjects/Account/{sf_id}
  - get_opportunities: GET /services/data/v57.0/query?q=SELECT+Id,Name,StageName,
    Amount,CloseDate,Type,Probability+FROM+Opportunity+WHERE+AccountId='{id}'
  - get_contacts: GET /services/data/v57.0/query?q=SELECT+...+FROM+Contact+WHERE+AccountId='{id}'
  - get_activities: GET /services/data/v57.0/query?q=SELECT+...+FROM+ActivityHistory+
    WHERE+WhatId='{id}'+AND+ActivityDate>=LAST_N_DAYS:{days}
  - Auth: POST /services/oauth2/token (client_credentials) → Bearer token

- [x] **T4A.2 — SalesforceMapper**
File: mcp/adapters/crm/salesforce/salesforce_mapper.py
- map_account(raw) → CanonicalAccount
  - Id → crm_source_id, AccountNumber used for canonical_account_id hash
  - Industry → industry (direct map)
  - NumberOfEmployees → employee_count
  - AnnualRevenue → account_value
  - BillingCountry → region
- map_opportunity(raw) → CanonicalOpportunity
  - StageName → OpportunityStage (map: "Prospecting"→prospecting, "Closed Won"→won, etc.)
  - Type → OpportunityType
- map_contact(raw) → CanonicalContact
  - Title → infer ContactRole (CEO/CFO/VP → economic_buyer, Engineer → technical_evaluator)
- map_activity(raw) → CanonicalActivity
  - TaskSubtype/Type → ActivityType
  - Description keywords → Sentiment

- [x] **T4A.3 — DynamicsMCP (FULL)**
File: mcp/adapters/crm/dynamics/dynamics_mcp.py
- Mock: same 3 seed accounts, Dynamics field naming convention
  (accountid, name, industrycode, revenue, numberofemployees, ownerid)
- Real: Microsoft Dataverse API
  - get_account: GET https://{org}.api.crm.dynamics.com/api/data/v9.2/accounts({guid})
    ?$select=accountid,name,industrycode,revenue,numberofemployees
  - get_opportunities: GET /api/data/v9.2/opportunities?$filter=_accountid_value eq {guid}
    &$select=opportunityid,name,statecode,estimatedvalue,estimatedclosedate,opportunityratingcode
  - get_contacts: GET /api/data/v9.2/contacts?$filter=_accountid_value eq {guid}
  - get_activities: GET /api/data/v9.2/activitypointers?$filter=_regardingobjectid_value eq {guid}
    &$filter=actualend ge {cutoff_date}
  - Auth: MSAL client_credentials using tenant_id + client_id + client_secret

- [x] **T4A.4 — DynamicsMapper**
- map_account: industrycode (int enum) → industry string
- map_opportunity: statecode (0=Open,1=Won,2=Lost) → OpportunityStage
- map_contact: jobtitle → ContactRole inference

- [x] **T4A.5 — OracleCRMMCP (FULL)**
File: mcp/adapters/crm/oracle_crm/oracle_crm_mcp.py
- Mock: same 3 accounts, Oracle CX Sales naming (PartyId, PartyName, PrimaryAddress)
- Real: Oracle CX Sales REST
  - get_account: GET /crmRestApi/resources/latest/accounts/{party_id}
  - get_opportunities: GET /crmRestApi/resources/latest/opportunities?q=AccountId={id}
  - get_contacts: GET /crmRestApi/resources/latest/contacts?q=AccountId={id}
  - get_activities: GET /crmRestApi/resources/latest/activities?q=AccountId={id}
  - Auth: Basic auth (username:password base64) or OCI API key

- [x] **T4A.6 — OracleCRMMapper**
- PartyId → crm_source_id
- PrimaryAddress.Country → region
- IndustryCode → industry (Oracle industry code lookup table)

- [x] **T4A.7 — Tests for all 3 CRM adapters (tests/test_crm_adapters.py)**
- Each adapter: mock returns valid data for all 3 seed accounts
- Each tool returns schema matching abstract interface
- Each mapper produces valid CanonicalAccount/Opportunity/Contact/Activity
- All 3 mappers produce IDENTICAL canonical output for same underlying account data
- Timeout raises MCPTimeoutError for all 3

### 4B — CPQ Adapter

- [x] **T4B.1 — OracleCPQMCP (FULL)**
File: mcp/adapters/cpq/oracle_cpq/oracle_cpq_mcp.py
- Mock product catalog: 8 products across 3 categories
  - Product 1: EnterpriseCore (enterprise, $60K/yr base)
  - Product 2: AnalyticsPro (enterprise, $24K/yr addon)
  - Product 3: SecurityBundle (all segments, $18K/yr)
  - Product 4: MidMarketSuite (mid_market, $28K/yr)
  - Product 5: APIAccess (all, $12K/yr)
  - Product 6: SupportPremium (all, $8K/yr)
  - Product 7: OnboardingServices (all, $5K one-time)
  - Product 8: TrainingBundle (all, $3K one-time)
- Mock pricing tiers: volume discount for >100 seats, >500 seats
- Mock margin floors: 18% minimum, 25% approval threshold
- Real: Oracle CPQ REST API
  - get_product_catalog: GET /rest/v1/catalogs/{catalog_id}/products
  - get_pricing_context: POST /rest/v1/priceList/calculate
  - create_quote_draft: POST /rest/v1/quotes
  - Auth: Oracle CPQ API key in X-API-KEY header

- [x] **T4B.2 — OracleCPQMapper → CanonicalProduct + CanonicalQuote**

- [x] **T4B.3 — Tests (tests/test_cpq_adapter.py)**
- Catalog returns 8 products
- Pricing context returns tiers for each segment
- Mapper produces valid CanonicalProduct for all 8

### 4C — OMS Adapters

- [x] **T4C.1 — OracleFOMMCP (FULL)**
File: mcp/adapters/oms/oracle_fom/oracle_fom_mcp.py
- Mock: 2-3 orders per seed account, Oracle FOM schema
  (OrderNumber, OrderType, Status, OrderedDate, TotalOrderedAmount, Lines[])
- Real: OIC REST integration endpoint
  GET {oracle_fom_oic_url}/orders?accountId={id}
- OracleFOMMapper: maps FOM schema → CanonicalOrder + OrderLineItem

- [x] **T4C.2 — SalesforceOMSMCP (FULL mock)**
File: mcp/adapters/oms/salesforce_oms/salesforce_oms_mcp.py
- Mock: same 3 accounts, Salesforce Order schema
  (Id, OrderNumber, Status, EffectiveDate, TotalAmount, OrderItems[])
- Real stub: documented with Salesforce OMS REST API endpoint + auth pattern
  GET /services/data/v57.0/query?q=SELECT+...+FROM+Order+WHERE+AccountId='{id}'
  Note: reuses same Salesforce OAuth2 credentials as SalesforceMCP CRM adapter

- [x] **T4C.3 — SAPOMSMCP (FULL mock)**
File: mcp/adapters/oms/sap_oms/sap_oms_mcp.py
- Mock: SAP sales order schema
  (SalesOrder, SalesOrderType, SoldToParty, TotalNetAmount, SalesOrderItem[])
- Real stub: SAP OData API
  GET https://{sap_host}/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder
  ?$filter=SoldToParty eq '{party_id}'&$expand=to_Item
  Auth: SAP Basic auth (client/username/password) or OAuth2

- [x] **T4C.4 — ZuoraOMSMCP (FULL mock)**
File: mcp/adapters/oms/zuora_oms/zuora_oms_mcp.py
- Mock: Zuora order schema (orderId, orderNumber, status, orderDate,
  lineItems[{orderLineItemId, quantity, unitPrice, amountWithoutTax}])
- Real stub: GET https://rest.zuora.com/v1/orders?accountKey={key}
  Auth: POST https://rest.zuora.com/oauth/token (client_credentials)

- [x] **T4C.5 — NetsuiteOMSMCP (FULL mock)**
File: mcp/adapters/oms/netsuite_oms/netsuite_oms_mcp.py
- Mock: NetSuite sales order schema (id, tranId, entity, total, status,
  item[{item, quantity, rate, amount}])
- Real stub: GET /services/rest/record/v1/salesorder?q=entity IS {entity_id}
  Auth: OAuth1 TBA (tokenId + tokenSecret + consumerKey)

- [x] **T4C.6 — OMS Mappers** — all 5 map to CanonicalOrder + OrderLineItem
- All mappers produce IDENTICAL canonical output for same underlying order data
- order_type normalization: vendor-specific status strings → OrderType enum
- status normalization: vendor-specific → OrderStatus enum

- [x] **T4C.7 — Tests (tests/test_oms_adapters.py)**
- All 5 adapters return mock data for all 3 seed accounts
- All 5 mappers produce valid CanonicalOrder objects
- All 5 mappers produce IDENTICAL output for same logical order

### 4D — Sub Adapters

- [x] **T4D.1 — OracleSubMCP (FULL)**
File: mcp/adapters/sub/oracle_sub/oracle_sub_mcp.py
- Mock: Oracle Subscription Cloud schema
  (SubscriptionId, ProductId, StatusCode, StartDate, EndDate, TotalAmount,
   UsageMetrics{currentUsage, entitledUsage, percentUsed})
- Real: OIC endpoint GET {oracle_sub_oic_url}/subscriptions?accountId={id}

- [x] **T4D.2 — ZuoraSubMCP (FULL mock)**
File: mcp/adapters/sub/zuora_sub/zuora_sub_mcp.py
- Mock: Zuora subscription schema
  (id, subscriptionNumber, status, contractedMrr, termStartDate, termEndDate,
   ratePlans[{productName, charges[{chargeType, price}]}],
   usageSummary{totalUsage, usageLimit, utilizationPct})
- Real stub: GET https://rest.zuora.com/v1/subscriptions/accounts/{key}

- [x] **T4D.3 — ChargebeeMCP (FULL mock)**
File: mcp/adapters/sub/chargebee/chargebee_mcp.py
- Mock: Chargebee subscription schema
  (id, customer_id, status, plan_id, plan_amount, current_term_start,
   current_term_end, usage_records[{id, quantity, usage_date}])
- Real stub: GET https://{site}.chargebee.com/api/v2/subscriptions?customer_id[is]={id}
  Auth: Basic auth with api_key as password, empty username

- [x] **T4D.4 — SalesforceRevenueMCP (FULL mock)**
File: mcp/adapters/sub/salesforce_revenue/salesforce_rev_mcp.py
- Mock: Salesforce Revenue Cloud / CPQ subscription schema
  (Id, SBQQ__Account__c, SBQQ__Product__c, SBQQ__Quantity__c, SBQQ__StartDate__c,
   SBQQ__EndDate__c, SBQQ__NetPrice__c, SBQQ__SubscriptionStatus__c)
- Real stub: GET /services/data/v57.0/query?q=SELECT+...+FROM+SBQQ__Subscription__c
  +WHERE+SBQQ__Account__c='{id}'
  Auth: reuses Salesforce OAuth2 credentials

- [x] **T4D.5 — Sub Mappers** — all 4 map to CanonicalSubscription
- renewal_date computed from termEndDate/EndDate/current_term_end
- usage_health_score normalized from usagePercent/utilizationPct
- usage_trend derived from usage history records (if available) else STABLE
- status normalization: vendor-specific → SubscriptionStatus enum

- [x] **T4D.6 — Tests (tests/test_sub_adapters.py)**
- All 4 adapters return valid mock data for all 3 seed accounts
- All 4 mappers produce valid CanonicalSubscription
- renewal_date is present in all 4 outputs
- usage_health_score in 0.0–1.0 range for all

### 4E — Install Base Adapter

- [x] **T4E.1 — OracleInstallBaseMCP (FULL mock)**
File: mcp/adapters/install_base/oracle_install_base_mcp.py
- Tool: get_installed_products(account_id) → list[dict]
- Mock schema: {instanceId, productId, productName, quantity, installDate,
   location, supportLevel, endOfSupportDate}
- Seed: 2-4 installed products per account (matches contracted_products in subscription)
- Real stub: GET /installBase/rest/v1/instances?partyId={party_id}
  Auth: Oracle API key

- [x] **T4E.2 — OracleInstallBaseMapper → list[InstalledProduct]**

- [x] **T4E.3 — Tests (tests/test_install_base_adapter.py)**

### 4F — MCPFactory

- [x] **T4F.1** Implement MCPFactory in mcp/factory.py
- get_crm_server() → correct CRM adapter (3 options)
- get_cpq_server() → OracleCPQMCP (always)
- get_oms_server() → correct OMS adapter (5 options)
- get_sub_server() → correct Sub adapter (4 options)
- get_install_base_server() → OracleInstallBaseMCP
- Singleton per settings via @lru_cache(maxsize=1)
- ConfigurationError on unknown provider enum

- [x] **T4F.2** Tests — all 13 provider combinations return correct adapter type

**Acceptance (Phase 4 complete):** All adapter tests pass, all 14 adapters return
valid mock data for all 3 seed accounts, all mappers produce identical canonical
output regardless of source adapter. 80% coverage on mcp/.

---

## Phase 5 — Context Assembly Layer

- [x] **T5.1** ContextAssembler (context/assembler.py)
  - Concurrent pull: asyncio.gather(crm, cpq, oms, sub, install_base, return_exceptions=True)
  - Per-source timeout from settings
  - Handle exceptions: MCPTimeoutError + MCPConnectionError → missing_sources
  - Call Normalizer after each successful source
  - Call ConflictResolver on normalized results
  - Call RenewalSignalBuilder
  - Call ContextValidator
  - Set context_run_id, assembled_at, all provider fields
  - NEVER raise — always return UnifiedContext

- [x] **T5.2** Normalizer (context/normalizer.py)
  - normalize_crm(raw, provider) → CanonicalAccount + Opportunity + Contacts + Activities
  - normalize_cpq(raw) → list[CanonicalProduct]
  - normalize_oms(raw, provider) → list[CanonicalOrder]
  - normalize_sub(raw, provider) → CanonicalSubscription
  - normalize_install_base(raw) → list[InstalledProduct]
  - Delegates to the correct mapper via provider enum

- [x] **T5.3** ConflictResolver (context/conflict_resolver.py)
  - resolve(context_parts) → (resolved_dict, list[ConflictResolution])
  - Rules: account_value HIGHER, close_date SUB, renewal_date SUB,
    industry MORE_SPECIFIC, account_name CRM, opportunity_stage MOST_ADVANCED
  - Record ConflictResolution for every resolved field

- [x] **T5.4** ContextValidator (context/validator.py)
  - Required fields check → COMPLETE | PARTIAL | DEGRADED
  - Required: account.canonical_account_id, account.account_value,
    subscription.renewal_date OR opportunity.close_date,
    subscription.status, subscription.usage_health_score

- [x] **T5.5** Tests (tests/test_context_assembly.py)
  - All 5 sources up → COMPLETE
  - Sub timeout → PARTIAL
  - Sub + OMS timeout → DEGRADED
  - Conflict: account_value → higher wins + ConflictResolution recorded
  - Conflict: renewal_date → subscription wins
  - Each of the 12 vendor combinations (3 CRM × 4 Sub) produces same canonical output

**Acceptance:** All tests pass, 80% coverage on context/

---

## Phase 6 — Seed Data

- [x] **T6.1** Create seed_data/ JSON files
  - accounts.json: ACC-001/002/003 with all vendor-specific field versions
    (one entry per account, with subkeys per vendor: sf_fields, dynamics_fields,
    oracle_crm_fields used by each adapter's mock)
  - opportunities.json: one open renewal opp per account × 3 CRM schemas
  - contacts.json: 2-3 contacts per account × 3 CRM schemas
  - subscriptions.json: one subscription per account × 4 Sub schemas
  - orders.json: 2-3 orders per account × 5 OMS schemas
  - activities.json: 8 activities per account × 3 CRM schemas
  - install_base.json: 2-4 installed products per account

- [x] **T6.2** Data contract: all adapters load from seed_data/ — no hardcoded fixtures

- [x] **T6.3** Seeder script: python -m seed_data.seeder loads SQLite for demo runs

**Acceptance:** make seed completes, all adapters return data for all 3 accounts

---

## Phase 7 — Agents

- [x] **T7.1** RenewalSignalBuilder (agents/renewal_signal_builder.py)
  - risk_score = weighted(usage_health*0.4 + escalations*0.25 + urgency*0.2 + sentiment*0.15)
  - risk_tier from score bands
  - churn_indicators: usage_critical, usage_declining, multiple_escalations,
    late_stage_risk, negative_sentiment_trend
  - upsell_propensity from usage + expansion recency + product gaps vs CPQ catalog
  - expansion_products: eligible items from CPQ not in contracted_products
  - recommended_action from risk_tier + upsell_propensity matrix

- [x] **T7.2** DecisionAgent (agents/decision_agent.py)
  - Calls RenewalSignalBuilder
  - Pricing: base_price * risk_adjustment (CRITICAL 0.88, HIGH 0.93, MEDIUM 0.97, LOW 1.0)
  - Margin guardrail: clamp to min_margin_floor if needed
  - Approval: set if discount > approval_discount_threshold
  - Expansion offer: if upsell_propensity > 0.65 + eligible products exist
  - Confidence: complete | partial | degraded from context_completeness
  - decision_flag: none | requires_human_review | proposal_locked
  - reasoning_steps: human-readable list of all decision steps

- [x] **T7.3** AgentDecision Pydantic model

- [x] **T7.4** Tests (tests/test_decision_agent.py)
  - ACC-001 HIGH risk → risk_adjusted_renewal, $79,500
  - ACC-002 LOW risk → standard_renewal + expansion_offer
  - ACC-003 CRITICAL risk → escalate_to_csm, proposal_locked
  - PARTIAL context → requires_human_review
  - Margin floor enforced (price never below floor)

---

## Phase 8 — Audit Store

- [x] **T8.1** SQLAlchemy ORM models (audit/models.py)
  - context_runs, conflict_records, agent_runs, source_calls tables

- [x] **T8.2** AuditStore (audit/audit_store.py)
  - save_context_run, save_agent_run, get_context_run, get_agent_runs

- [x] **T8.3** Tests: round-trip save + retrieve

---

## Phase 9 — API Layer

- [x] **T9.1** api/main.py — FastAPI app, lifespan DB init, CORS, all routers

- [x] **T9.2** context.py router — /context/assemble, /context/{id}, /context/compare

- [x] **T9.3** agent.py router — /agent/run (with SSE stream), /agent/runs

- [x] **T9.4** audit.py router — /audit/{context_run_id}

- [x] **T9.5** settings.py router — GET/POST /settings (hot-swap providers), GET /readiness
  - /readiness calls each of the 14 adapters with a health-check tool call
  - Returns per-adapter: name, provider, mode, status (green/yellow/red), latency_ms

- [x] **T9.6** demo.py router — POST /demo/{1-6} runs named scenario

- [x] **T9.7** Tests (tests/test_api.py) — all endpoints happy path + error cases

---

## Phase 10 — Demo Scenarios

- [x] **T10.1** DemoRunner (demo/runner.py)
- [x] **T10.2** scenario_1_snapshot_vs_live.py — ACC-001, stale vs live
- [x] **T10.3** scenario_2_sf_to_oracle.py — ACC-002, Salesforce + Oracle FOM + Oracle Sub
- [x] **T10.4** scenario_3_dynamics_to_oracle.py — ACC-002, Dynamics same expected output
- [x] **T10.5** scenario_4_sap_zuora.py — ACC-003, Oracle CRM + SAP OMS + Zuora Sub
- [x] **T10.6** scenario_5_full_stack_variation.py — ACC-001, Salesforce + Zuora OMS + Chargebee
- [x] **T10.7** scenario_6_degraded.py — ACC-003, subscription timeout → PARTIAL

**Acceptance:** make demo runs scenario 1 with clean output showing stale vs live diff

---

## Phase 11 — Frontend

- [x] **T11.1** Scaffold React 18 + Vite + TypeScript + Tailwind in ui/
- [x] **T11.2** Typed API client (ui/src/api/client.ts)
- [x] **T11.3** About.tsx — business problem content from About_BusinessProblem.html
  - 6 sections: The Problem / Why It's Hard / The Solution / What It Solves /
    Production Proof / Who This Is For
  - Reuse the exact content and structure from the HTML file
- [x] **T11.4** StackConfigurator.tsx — ALL vendor options selectable
  - CRM selector: Salesforce | MS Dynamics 365 | Oracle CX Sales
  - CPQ: Oracle CPQ Cloud (display only — not selectable)
  - OMS selector: Oracle FOM | Salesforce OMS | SAP S/4HANA | Zuora | NetSuite
  - Sub selector: Oracle Sub Cloud | Zuora | Chargebee | Salesforce Revenue Cloud
  - Install Base: enable/disable toggle
  - Live preview: adapter filename + real API endpoint + auth method
  - Readiness badges per source (calls GET /readiness)
  - Calls POST /settings on change
  - "Vendor Adapters — plug in any combination" as header
- [x] **T11.5** ContextExplorer.tsx — account selector → assemble → show UnifiedContext
- [x] **T11.6** SnapshotDemo.tsx — side-by-side stale vs live with diff highlighting
- [x] **T11.7** AgentRuns.tsx — decision history + expandable audit trail
- [x] **T11.8** Architecture.tsx — system diagram, all 4 layers, all 14 adapter slots,
  active adapters highlighted in green
- [x] **T11.9** App.tsx router — 6 pages with nav sidebar

---

## Phase 12 — README + Polish

- [x] **T12.1** README.md with: description, business problem, vendor support matrix,
  quick start (4 commands), 6 scenario table, stack table, repo structure

- [x] **T12.2** Final test run — all tests pass, 80%+ coverage

- [x] **T12.3** Docker build succeeds

- [x] **T12.4** Run all 6 demo scenarios, verify outputs match expected decisions

- [x] **T12.5** All 6 UI pages load and function
