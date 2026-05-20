/* Author: Sarala Biswal */
/* Code documentation: Scenario and Vendor Stack page for selecting demo stories and runtime provider combinations. */
import { useEffect, useMemo, useRef, useState } from 'react';
import { PageId, Scenario } from '../App';
import { apiGet, apiPost, DemoResult, Readiness, StackSettings } from '../api/client';
import { EvidenceDrawer, PageHeader, StatusPill } from '../components/Presentation';

type AdapterMeta = {
  layer: 'CRM' | 'CPQ' | 'OMS' | 'Subscription' | 'Install Base';
  provider: string;
  label: string;
  file: string;
  endpoint: string;
  auth: string;
  businessRole: string;
  canonicalObjects: string[];
};

const adapterMeta: AdapterMeta[] = [
  {
    layer: 'CRM',
    provider: 'salesforce',
    label: 'Salesforce CRM',
    file: 'salesforce_mcp.py',
    endpoint: '/services/data/v57.0',
    auth: 'OAuth2',
    businessRole: 'Customer, opportunity, relationship owner, activity sentiment',
    canonicalObjects: ['Account', 'Opportunity', 'Contact', 'Activity'],
  },
  {
    layer: 'CRM',
    provider: 'dynamics',
    label: 'MS Dynamics 365',
    file: 'dynamics_mcp.py',
    endpoint: '/api/data/v9.2',
    auth: 'Azure AD',
    businessRole: 'Customer, opportunity, relationship owner, activity sentiment',
    canonicalObjects: ['Account', 'Opportunity', 'Contact', 'Activity'],
  },
  {
    layer: 'CRM',
    provider: 'oracle_crm',
    label: 'Oracle CX Sales',
    file: 'oracle_crm_mcp.py',
    endpoint: '/crmRestApi/resources/latest',
    auth: 'Basic or OCI key',
    businessRole: 'Customer, opportunity, relationship owner, activity sentiment',
    canonicalObjects: ['Account', 'Opportunity', 'Contact', 'Activity'],
  },
  {
    layer: 'CPQ',
    provider: 'oracle_cpq',
    label: 'Oracle CPQ Cloud',
    file: 'oracle_cpq_mcp.py',
    endpoint: '/rest/v1/quotes',
    auth: 'X-API-KEY',
    businessRole: 'Quote baseline, product catalog, list price, margin guardrails',
    canonicalObjects: ['Quote', 'Product', 'PriceBook'],
  },
  {
    layer: 'OMS',
    provider: 'oracle_fom',
    label: 'Oracle FOM',
    file: 'oracle_fom_mcp.py',
    endpoint: '/orders?accountId=',
    auth: 'Oracle Integration Cloud REST credentials',
    businessRole: 'Open orders, fulfillment state, order value, delivery risk',
    canonicalObjects: ['Order', 'OrderLine', 'FulfillmentStatus'],
  },
  {
    layer: 'OMS',
    provider: 'salesforce_oms',
    label: 'Salesforce Order Management',
    file: 'salesforce_oms_mcp.py',
    endpoint: '/services/data/v57.0/query',
    auth: 'OAuth2',
    businessRole: 'Open orders, fulfillment state, order value, delivery risk',
    canonicalObjects: ['Order', 'OrderLine', 'FulfillmentStatus'],
  },
  {
    layer: 'OMS',
    provider: 'sap_s4hana',
    label: 'SAP S/4HANA',
    file: 'sap_oms_mcp.py',
    endpoint: '/sap/opu/odata/sap/API_SALES_ORDER_SRV',
    auth: 'Basic or OAuth2',
    businessRole: 'Open orders, fulfillment state, order value, delivery risk',
    canonicalObjects: ['Order', 'OrderLine', 'FulfillmentStatus'],
  },
  {
    layer: 'OMS',
    provider: 'zuora_oms',
    label: 'Zuora Order Management',
    file: 'zuora_oms_mcp.py',
    endpoint: '/v1/orders',
    auth: 'OAuth2',
    businessRole: 'Open orders, fulfillment state, order value, delivery risk',
    canonicalObjects: ['Order', 'OrderLine', 'FulfillmentStatus'],
  },
  {
    layer: 'OMS',
    provider: 'netsuite',
    label: 'NetSuite Order Management',
    file: 'netsuite_oms_mcp.py',
    endpoint: '/services/rest/record/v1/salesorder',
    auth: 'OAuth1 TBA',
    businessRole: 'Open orders, fulfillment state, order value, delivery risk',
    canonicalObjects: ['Order', 'OrderLine', 'FulfillmentStatus'],
  },
  {
    layer: 'Subscription',
    provider: 'oracle_subscription',
    label: 'Oracle Sub Cloud',
    file: 'oracle_sub_mcp.py',
    endpoint: '/subscriptions?accountId=',
    auth: 'Oracle Integration Cloud REST credentials',
    businessRole: 'ARR, renewal date, usage health, escalation posture',
    canonicalObjects: ['Subscription', 'UsageHealth', 'RenewalSignal'],
  },
  {
    layer: 'Subscription',
    provider: 'zuora_sub',
    label: 'Zuora Sub',
    file: 'zuora_sub_mcp.py',
    endpoint: '/v1/subscriptions/accounts',
    auth: 'OAuth2',
    businessRole: 'ARR, renewal date, usage health, escalation posture',
    canonicalObjects: ['Subscription', 'UsageHealth', 'RenewalSignal'],
  },
  {
    layer: 'Subscription',
    provider: 'chargebee',
    label: 'Chargebee',
    file: 'chargebee_mcp.py',
    endpoint: '/api/v2/subscriptions',
    auth: 'API key',
    businessRole: 'ARR, renewal date, usage health, escalation posture',
    canonicalObjects: ['Subscription', 'UsageHealth', 'RenewalSignal'],
  },
  {
    layer: 'Subscription',
    provider: 'salesforce_revenue',
    label: 'Salesforce Revenue Cloud',
    file: 'salesforce_rev_mcp.py',
    endpoint: '/services/data/v57.0/query',
    auth: 'OAuth2',
    businessRole: 'ARR, renewal date, usage health, escalation posture',
    canonicalObjects: ['Subscription', 'UsageHealth', 'RenewalSignal'],
  },
  {
    layer: 'Install Base',
    provider: 'oracle_install_base',
    label: 'Oracle Install Base',
    file: 'oracle_install_base_mcp.py',
    endpoint: '/installBase/rest/v1/instances',
    auth: 'Oracle API key',
    businessRole: 'Installed products, quantities, locations, support entitlement',
    canonicalObjects: ['InstalledProduct', 'Entitlement'],
  },
  {
    layer: 'Install Base',
    provider: 'salesforce_asset',
    label: 'Salesforce Asset Management',
    file: 'salesforce_asset_mcp.py',
    endpoint: '/services/data/v57.0/query',
    auth: 'OAuth2',
    businessRole: 'Customer assets, product ownership, entitlement and support coverage',
    canonicalObjects: ['InstalledProduct', 'Entitlement'],
  },
  {
    layer: 'Install Base',
    provider: 'servicenow_cmdb',
    label: 'ServiceNow CMDB',
    file: 'servicenow_cmdb_mcp.py',
    endpoint: '/api/now/table/cmdb_ci',
    auth: 'OAuth2 or Basic',
    businessRole: 'Configuration items, deployed products, locations, and service entitlement',
    canonicalObjects: ['InstalledProduct', 'Entitlement'],
  },
];

const layerOrder: AdapterMeta['layer'][] = ['CRM', 'CPQ', 'OMS', 'Subscription', 'Install Base'];
const layerDisplayName: Record<AdapterMeta['layer'], string> = {
  CRM: 'CRM',
  CPQ: 'CPQ',
  OMS: 'Order Management Systems',
  Subscription: 'Subscription',
  'Install Base': 'Install Base',
};

const scenarioStackSettings: Record<number, Partial<StackSettings>> = {
  1: {
    crm_provider: 'salesforce',
    oms_provider: 'oracle_fom',
    sub_provider: 'oracle_subscription',
    install_base_provider: 'oracle_install_base',
    install_base_enabled: true,
  },
  2: {
    crm_provider: 'salesforce',
    oms_provider: 'oracle_fom',
    sub_provider: 'oracle_subscription',
    install_base_provider: 'oracle_install_base',
    install_base_enabled: true,
  },
  3: {
    crm_provider: 'dynamics',
    oms_provider: 'oracle_fom',
    sub_provider: 'oracle_subscription',
    install_base_provider: 'oracle_install_base',
    install_base_enabled: true,
  },
  4: {
    crm_provider: 'oracle_crm',
    oms_provider: 'sap_s4hana',
    sub_provider: 'zuora_sub',
    install_base_provider: 'servicenow_cmdb',
    install_base_enabled: true,
  },
  5: {
    crm_provider: 'salesforce',
    oms_provider: 'zuora_oms',
    sub_provider: 'chargebee',
    install_base_provider: 'salesforce_asset',
    install_base_enabled: true,
  },
  6: {
    crm_provider: 'salesforce',
    oms_provider: 'oracle_fom',
    sub_provider: 'oracle_subscription',
    install_base_provider: 'oracle_install_base',
    install_base_enabled: true,
  },
  7: {
    crm_provider: 'salesforce',
    oms_provider: 'oracle_fom',
    sub_provider: 'oracle_subscription',
    install_base_provider: 'oracle_install_base',
    install_base_enabled: true,
  },
};

const scenarioProof: Record<number, string> = {
  1: 'Shows why live commercial context can change the risk posture compared with a stale snapshot.',
  2: 'Shows a healthy renewal where the agent can keep standard pricing and include expansion.',
  3: 'Uses the same account as Scenario 2 and swaps CRM to prove vendor-equivalent facts produce the same decision.',
  4: 'Runs a non-Salesforce stack and shows a critical escalation branch with a locked proposal.',
  5: 'Runs the TechCorp account through mixed Order Management Systems and subscription vendors to prove stack portability.',
  6: 'Simulates missing subscription context so governance routes the decision to human review.',
  7: 'Adds a high-risk account with no expansion fit so the agent selects a save-play motion.',
};

const scenarioBranch: Record<number, { label: string; tone: 'good' | 'warn' | 'danger' | 'neutral' }> = {
  1: { label: 'Risk-adjusted renewal', tone: 'danger' },
  2: { label: 'Standard + expansion', tone: 'good' },
  3: { label: 'Vendor-equivalent decision', tone: 'good' },
  4: { label: 'Critical escalation', tone: 'danger' },
  5: { label: 'Mixed-stack parity', tone: 'warn' },
  6: { label: 'Human review', tone: 'warn' },
  7: { label: 'Save play', tone: 'danger' },
};

type Props = {
  activePage: PageId;
  scenario: Scenario;
  scenarios: Scenario[];
  setScenarioId: (id: number) => void;
  goTo: (page: PageId) => void;
  requestDecisionRun?: () => void;
};

export default function ScenarioWalkthrough({ activePage, scenario, scenarios, setScenarioId, goTo, requestDecisionRun }: Props) {
  const [settings, setSettings] = useState<Partial<StackSettings>>({});
  const [readiness, setReadiness] = useState<Readiness[]>([]);
  const [demo, setDemo] = useState<DemoResult | null>(null);
  const [runLoading, setRunLoading] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const selectedScenarioIdRef = useRef(scenario.id);

  useEffect(() => {
    apiGet<StackSettings>('/settings').then(setSettings);
    apiGet<Readiness[]>('/readiness').then(setReadiness);
  }, []);

  useEffect(() => {
    selectedScenarioIdRef.current = scenario.id;
  }, [scenario.id]);

  const active = useMemo(
    () =>
      new Set([
        settings.crm_provider ?? 'salesforce',
        'oracle_cpq',
        settings.oms_provider ?? 'oracle_fom',
        settings.sub_provider ?? 'oracle_subscription',
        settings.install_base_provider ?? 'oracle_install_base',
      ]),
    [settings],
  );
  const selectedAdapters = layerOrder
    .map((layer) => adapterMeta.find((adapter) => adapter.layer === layer && active.has(adapter.provider)))
    .filter((adapter): adapter is AdapterMeta => Boolean(adapter));
  const activeAdapterByLayer = new Map(selectedAdapters.map((adapter) => [adapter.layer, adapter]));
  const adaptersByLayer = layerOrder.map((layer) => ({
    layer,
    adapters: adapterMeta.filter((adapter) => adapter.layer === layer),
  }));
  const readinessByProvider = new Map(readiness.map((item) => [item.provider, item]));
  const activeVendorCount = selectedAdapters.length;

  async function patchSettings(patch: Partial<StackSettings>) {
    const next = await apiPost<StackSettings>('/settings', patch);
    setSettings(next);
    setReadiness(await apiGet<Readiness[]>('/readiness'));
  }

  async function update(key: string, value: string | boolean) {
    await patchSettings({ [key]: value } as Partial<StackSettings>);
  }

  async function selectAdapter(adapter: AdapterMeta) {
    if (adapter.layer === 'CPQ') return;
    if (adapter.layer === 'CRM') await patchSettings({ crm_provider: adapter.provider as StackSettings['crm_provider'] });
    if (adapter.layer === 'OMS') await patchSettings({ oms_provider: adapter.provider as StackSettings['oms_provider'] });
    if (adapter.layer === 'Subscription') await patchSettings({ sub_provider: adapter.provider as StackSettings['sub_provider'] });
    if (adapter.layer === 'Install Base') {
      await patchSettings({ install_base_enabled: true, install_base_provider: adapter.provider as StackSettings['install_base_provider'] });
    }
  }

  async function selectScenario(id: number) {
    selectedScenarioIdRef.current = id;
    setDemo(null);
    setRunError(null);
    setScenarioId(id);
    const next = await apiPost<StackSettings>('/settings', scenarioStackSettings[id]);
    setSettings(next);
    setReadiness(await apiGet<Readiness[]>('/readiness'));
  }

  async function runScenario(id = selectedScenarioIdRef.current) {
    setRunLoading(true);
    setRunError(null);
    try {
      const selectedScenario = scenarios.find((item) => item.id === id) ?? scenario;
      const next = await apiPost<StackSettings>('/settings', scenarioStackSettings[id]);
      setSettings(next);
      const [demoResult] = await Promise.all([
        apiPost<DemoResult>(`/demo/${id}`, {}),
        apiPost('/agent/run', { account_id: selectedScenario.accountId }),
      ]);
      setDemo(demoResult);
    } catch (error) {
      setRunError(error instanceof Error ? error.message : 'Unable to run the selected scenario.');
    } finally {
      setRunLoading(false);
    }
  }

  async function reviewStack() {
    const next = await apiPost<StackSettings>('/settings', scenarioStackSettings[selectedScenarioIdRef.current]);
    setSettings(next);
    setReadiness(await apiGet<Readiness[]>('/readiness'));
    goTo('stack');
  }

  if (activePage === 'scenarios') {
    return (
      <div className="page-stack">
        <PageHeader
          eyebrow="Demo Story"
          title="Choose the renewal story to prove"
          subtitle="Each scenario is a business outcome. Vendor selection is explained on the Vendor Stack page so the story stays focused."
        >
          <button className="primary-action" onClick={() => runScenario()} disabled={runLoading}>
            {runLoading ? 'Running...' : demo ? 'Re-run Scenario' : 'Run Scenario'}
          </button>
          <button className="secondary-action" onClick={reviewStack}>Review Selected Stack</button>
        </PageHeader>

        {runError ? (
          <section className="business-card error-panel">
            <span className="kicker">Run failed</span>
            <p>{runError}</p>
          </section>
        ) : null}

        {demo ? (
          <section className="scenario-result">
            <div>
              <span className="kicker">Scenario result</span>
              <h2>{scenario.name}</h2>
              <p>{demo.account_id} · {scenario.stack}</p>
            </div>
            <div className="result-metrics">
              <article>
                <span>Risk</span>
                <strong>{demo.risk_tier.toUpperCase()}</strong>
              </article>
              <article>
                <span>Action</span>
                <strong>{demo.recommended_action}</strong>
              </article>
              <article>
                <span>Adjusted price</span>
                <strong>{Number(demo.adjusted_price).toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}</strong>
              </article>
              <article>
                <span>Completeness</span>
                <strong>{demo.context_completeness.toUpperCase()}</strong>
              </article>
            </div>
            <div className="button-row">
              <button className="primary-action" onClick={() => requestDecisionRun?.() ?? goTo('decision')}>Run Decision in Cockpit</button>
              <button className="secondary-action" onClick={() => goTo('audit')}>View Captured Audit</button>
            </div>
          </section>
        ) : null}

        <section className="scenario-workbench">
          <div className="scenario-catalogue">
            <div className="scenario-catalogue-header">
              <div>
                <span className="kicker">Scenario catalogue</span>
                <h2>Seven business paths through the same agent flow</h2>
              </div>
              <span>{scenarios.length} demo paths</span>
            </div>
            <div className="scenario-table">
              <div className="scenario-table-head">
                <span></span>
                <span>Story</span>
                <span>Variation</span>
                <span>Expected branch</span>
              </div>
              {scenarios.map((item) => {
                const branch = scenarioBranch[item.id] ?? { label: 'Decision branch', tone: 'neutral' as const };
                return (
                  <button
                    className={`scenario-row ${item.id === scenario.id ? 'selected' : ''}`}
                    key={item.id}
                    onClick={() => selectScenario(item.id)}
                  >
                    <span className="scenario-row-id">{String(item.id).padStart(2, '0')}</span>
                    <span className="scenario-row-story">
                      <strong>{item.name}</strong>
                      <small>{item.accountId} · {item.stack}</small>
                    </span>
                    <span className="scenario-row-variation">{item.pattern}</span>
                    <span className={`scenario-branch ${branch.tone}`}>{branch.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <aside className="selected-scenario-panel">
            <span className="kicker">Selected variation</span>
            <h2>{scenario.name}</h2>
            <p>{scenarioProof[scenario.id]}</p>
            <dl>
              <div>
                <dt>Account</dt>
                <dd>{scenario.accountId}</dd>
              </div>
              <div>
                <dt>Stack</dt>
                <dd>{scenario.stack}</dd>
              </div>
              <div>
                <dt>Pattern</dt>
                <dd>{scenario.pattern}</dd>
              </div>
              <div>
                <dt>Expected outcome</dt>
                <dd>{scenario.expected}</dd>
              </div>
            </dl>
            <div className="scenario-step-strip">
              <span>Assemble</span>
              <span>Decide</span>
              <span>Audit</span>
            </div>
            <div className="button-row">
              <button className="primary-action" onClick={() => runScenario()} disabled={runLoading}>
                {runLoading ? 'Running...' : demo ? 'Re-run Selected' : 'Run Selected'}
              </button>
              <button className="secondary-action" onClick={reviewStack}>Review Stack</button>
              <button className="secondary-action" onClick={() => goTo('context')}>Live Context</button>
            </div>
          </aside>
        </section>

        {demo ? <EvidenceDrawer title="Raw Scenario Evidence" data={demo} /> : null}
      </div>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Vendor Stack"
        title="Enterprise source stack for this decision"
        subtitle="Select the commercial systems for the scenario. The adapters change, but the DecisionAgent still receives the same UnifiedContext contract."
      >
        <button className="primary-action" onClick={() => goTo('context')}>Continue to Live Context</button>
      </PageHeader>

      <section className="vendor-story-strip">
        <article>
          <span>Business question</span>
          <strong>Can the same decision run across mixed enterprise stacks?</strong>
          <p>The demo changes CRM, Order Management Systems, subscription, and install-base implementations without changing agent logic.</p>
        </article>
        <article>
          <span>Architecture proof</span>
          <strong>Adapters normalize vendor records before the agent sees them</strong>
          <p>Salesforce, Dynamics, Oracle, SAP, Zuora, Chargebee, NetSuite, and ServiceNow map into one frozen canonical context.</p>
        </article>
      </section>

      <section className="vendor-stack-layout">
        <div className="vendor-stack-main">
          <section className="control-band stack-controls vendor-controls">
            <label>
              CRM
              <select value={settings.crm_provider ?? 'salesforce'} onChange={(event) => update('crm_provider', event.target.value)}>
                <option value="salesforce">Salesforce</option>
                <option value="dynamics">MS Dynamics 365</option>
                <option value="oracle_crm">Oracle CX Sales</option>
              </select>
            </label>
            <label>
              Order Management Systems
              <select value={settings.oms_provider ?? 'oracle_fom'} onChange={(event) => update('oms_provider', event.target.value)}>
                <option value="oracle_fom">Oracle FOM</option>
                <option value="salesforce_oms">Salesforce Order Management</option>
                <option value="sap_s4hana">SAP S/4HANA</option>
                <option value="zuora_oms">Zuora Order Management</option>
                <option value="netsuite">NetSuite Order Management</option>
              </select>
            </label>
            <label>
              Subscription
              <select value={settings.sub_provider ?? 'oracle_subscription'} onChange={(event) => update('sub_provider', event.target.value)}>
                <option value="oracle_subscription">Oracle Sub Cloud</option>
                <option value="zuora_sub">Zuora</option>
                <option value="chargebee">Chargebee</option>
                <option value="salesforce_revenue">Salesforce Revenue Cloud</option>
              </select>
            </label>
            <label>
              Install Base Provider
              <select
                value={settings.install_base_provider ?? 'oracle_install_base'}
                onChange={(event) => patchSettings({ install_base_enabled: true, install_base_provider: event.target.value as StackSettings['install_base_provider'] })}
              >
                <option value="oracle_install_base">Oracle Install Base</option>
                <option value="salesforce_asset">Salesforce Asset Management</option>
                <option value="servicenow_cmdb">ServiceNow CMDB</option>
              </select>
            </label>
          </section>

          <section className="selected-stack runtime-workbench">
            <div className="section-heading">
              <span className="kicker">Active runtime path</span>
              <h2>Components called for the current decision</h2>
              <p>Oracle CPQ stays fixed. The remaining system slots are selected by configuration and can be swapped from this page.</p>
            </div>
            <div className="runtime-lane">
              {selectedAdapters.map((adapter, index) => {
                const ready = readinessByProvider.get(adapter.provider);
                return (
                  <article className="runtime-node" key={adapter.provider}>
                    <div className="node-index">{String(index + 1).padStart(2, '0')}</div>
                    <div>
                      <div className="card-title-row">
                        <span>{layerDisplayName[adapter.layer]}</span>
                        <StatusPill label={ready?.status ?? 'yellow'} tone={ready?.status === 'red' ? 'danger' : 'good'} />
                      </div>
                      <h3>{adapter.label}</h3>
                      <p>{adapter.businessRole}</p>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="adapter-catalog vendor-slot-matrix">
            <div className="section-heading">
              <span className="kicker">Adapter slots</span>
              <h2>Pick any vendor implementation; keep the same canonical output</h2>
              <p>Use the compact matrix to see the active vendor, the interchangeable choices, and the exact objects the agent receives.</p>
            </div>
            <div className="slot-table">
              {adaptersByLayer.map(({ layer, adapters }, index) => {
                const activeAdapter = activeAdapterByLayer.get(layer);
                return (
                  <article className="slot-row" key={layer}>
                    <div className="slot-summary">
                      <span className="slot-index">{String(index + 1).padStart(2, '0')}</span>
                      <div>
                        <h3>{layerDisplayName[layer]}</h3>
                        <p>{layer === 'CPQ' ? 'Fixed quote engine' : 'Config-driven source slot'}</p>
                      </div>
                    </div>
                    <div className="slot-selected">
                      <span>Active implementation</span>
                      <strong>{activeAdapter?.label ?? 'Not enabled'}</strong>
                      <small>{activeAdapter?.auth ?? 'Install-base enrichment is disabled'}</small>
                    </div>
                    <div className="slot-alternatives">
                      {adapters.map((adapter) => {
                        const isActive = active.has(adapter.provider);
                        const ready = readinessByProvider.get(adapter.provider);
                        return (
                          <button
                            className={`slot-pill ${isActive ? 'selected' : ''}`}
                            key={adapter.provider}
                            onClick={() => selectAdapter(adapter)}
                            disabled={adapter.layer === 'CPQ'}
                            title={`${adapter.label} · ${adapter.endpoint}`}
                          >
                            <span>{adapter.label}</span>
                            <StatusPill label={ready?.status ?? 'yellow'} tone={ready?.status === 'red' ? 'danger' : 'good'} />
                          </button>
                        );
                      })}
                    </div>
                    <div className="slot-contract">
                      <span>Agent receives</span>
                      <div className="canonical-strip">
                        {adapters[0]?.canonicalObjects.map((object) => <strong key={object}>{object}</strong>)}
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        </div>

        <aside className="stack-proof-rail">
          <section>
            <span className="kicker">Scenario context</span>
            <h2>{scenario.name}</h2>
            <p>{scenario.accountId}</p>
            <strong>{scenario.stack}</strong>
          </section>
          <section>
            <span className="kicker">Current stack</span>
            <dl>
              <div>
                <dt>Selected components</dt>
                <dd>{activeVendorCount} of 5 slots</dd>
              </div>
              <div>
                <dt>Agent dependency</dt>
                <dd>UnifiedContext only</dd>
              </div>
              <div>
                <dt>Swap impact</dt>
                <dd>Adapter and source attribution</dd>
              </div>
            </dl>
          </section>
          <section className="proof-callout">
            <span>Why this matters</span>
            <p>When two vendors provide equivalent account, order, subscription, activity, and install-base facts, the canonical context is equivalent. That is why the same account data produces the same recommendation.</p>
          </section>
          <button className="primary-action" onClick={() => goTo('context')}>Assemble Live Context</button>
        </aside>
      </section>
    </div>
  );
}
