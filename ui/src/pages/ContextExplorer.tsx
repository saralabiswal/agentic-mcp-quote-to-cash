import { useEffect, useState } from 'react';
import { PageId, Scenario } from '../App';
import { apiPost, UnifiedContext } from '../api/client';
import {
  EvidenceDrawer,
  formatCurrency,
  PageHeader,
  percent,
  StatusPill,
} from '../components/Presentation';

type Props = {
  scenario: Scenario;
  goTo: (page: PageId) => void;
  requestDecisionRun?: () => void;
};

const labelFromPath = (value: string) =>
  value
    .split('.')
    .pop()
    ?.replace(/_/g, ' ')
    .replace(/\b\w/g, (letter: string) => letter.toUpperCase()) ?? value;

const labelFromRule = (value: string) =>
  value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter: string) => letter.toUpperCase());

const providerLabel = (value?: string) => {
  const labels: Record<string, string> = {
    salesforce: 'Salesforce',
    dynamics: 'MS Dynamics 365',
    oracle_crm: 'Oracle CX Sales',
    oracle_cpq: 'Oracle CPQ',
    oracle_fom: 'Oracle FOM',
    salesforce_oms: 'Salesforce Order Management',
    sap_s4hana: 'SAP S/4HANA',
    zuora_oms: 'Zuora Order Management',
    netsuite: 'NetSuite Order Management',
    oracle_subscription: 'Oracle Sub Cloud',
    zuora_sub: 'Zuora Sub',
    chargebee: 'Chargebee',
    salesforce_revenue: 'Salesforce Revenue Cloud',
    oracle_install_base: 'Oracle Install Base',
    salesforce_asset: 'Salesforce Asset Management',
    servicenow_cmdb: 'ServiceNow CMDB',
  };
  return labels[value ?? ''] ?? labelFromRule(value ?? 'unknown');
};

export default function LiveContext({ scenario, goTo, requestDecisionRun }: Props) {
  const [accountId, setAccountId] = useState(scenario.accountId);
  const [context, setContext] = useState<UnifiedContext | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setAccountId(scenario.accountId);
    setContext(null);
    setError(null);
  }, [scenario.accountId]);

  async function assemble() {
    setLoading(true);
    setError(null);
    try {
      setContext(await apiPost<UnifiedContext>('/context/assemble', { account_id: accountId }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to assemble context.');
    } finally {
      setLoading(false);
    }
  }

  function selectAccount(nextAccountId: string) {
    setAccountId(nextAccountId);
    setContext(null);
    setError(null);
  }

  const subscription = context?.subscription;
  const renewalSignal = context?.renewal_signal;
  const riskTone = renewalSignal?.risk_tier === 'high' || renewalSignal?.risk_tier === 'critical' ? 'danger' : 'good';
  const completenessTone = context?.context_completeness === 'complete' ? 'good' : 'warn';
  const installedProducts = context?.account.installed_base ?? [];
  const openOrderValue = context?.orders.reduce((total, order) => total + Number(order.total_amount ?? 0), 0) ?? 0;
  const sourceStack = context
    ? [
        ['CRM', providerLabel(context.crm_provider)],
        ['CPQ', 'Oracle CPQ'],
        ['Order Management Systems', providerLabel(context.oms_provider)],
        ['Subscription', providerLabel(context.sub_provider)],
        ['Install Base', installedProducts.length ? providerLabel(context.install_base_provider) : 'Not enabled'],
      ]
    : [];

  return (
    <div className="page-stack live-context-page">
      <PageHeader
        eyebrow="Live Context"
        title="Unified commercial truth assembled at decision time"
        subtitle="The ContextAssembler calls the active MCP adapters in parallel, resolves source conflicts, and returns the frozen UnifiedContext used by the DecisionAgent."
      >
        <button className="primary-action" onClick={assemble} disabled={loading}>
          {loading ? 'Assembling...' : context ? 'Reassemble Context' : 'Assemble Context'}
        </button>
        <button className="secondary-action" onClick={() => goTo('stack')}>Review Vendor Stack</button>
      </PageHeader>

      <section className="context-command">
        <div className="context-picker">
          <label>
            Context account
            <select value={accountId} onChange={(event) => selectAccount(event.target.value)}>
              <option value="ACC-001">ACC-001 · TechCorp Inc</option>
              <option value="ACC-002">ACC-002 · GlobalBanking Corp</option>
              <option value="ACC-003">ACC-003 · MidwestManufacturing</option>
              <option value="ACC-004">ACC-004 · RetailCo Stores</option>
            </select>
          </label>
          <button className="secondary-action" onClick={() => selectAccount(scenario.accountId)}>
            Use Story Account
          </button>
        </div>
        <div className="context-summary-card">
          <span>Story baseline</span>
          <strong>{scenario.name}</strong>
          <small>{scenario.accountId} · {scenario.pattern} · default stack: {scenario.stack}</small>
        </div>
        <div className="context-summary-card">
          <span>Assembly state</span>
          <strong>{context ? 'Context ready' : loading ? 'Assembling' : 'Not assembled'}</strong>
          <small>{context?.context_run_id ?? 'Choose an account, then assemble live context.'}</small>
        </div>
      </section>

      {error ? (
        <section className="business-card error-panel">
          <span className="kicker">Assembly failed</span>
          <p>{error}</p>
        </section>
      ) : null}

      {!context ? (
        <section className="context-empty">
          <div>
            <span className="kicker">Ready to assemble</span>
            <h2>Select an account, then assemble the live decision context</h2>
            <p>The result will show the normalized account, subscription, order, activity, CPQ, and install-base facts before the DecisionAgent prices the renewal.</p>
          </div>
          <div className="context-empty-steps">
            <article><strong>1</strong><span>Call active adapters</span></article>
            <article><strong>2</strong><span>Normalize to UnifiedContext</span></article>
            <article><strong>3</strong><span>Resolve source conflicts</span></article>
          </div>
          <button className="primary-action" onClick={assemble} disabled={loading}>
            {loading ? 'Assembling...' : 'Assemble Context'}
          </button>
        </section>
      ) : (
        <>
          <section className="context-briefing">
            <article className="account-brief">
              <span className="kicker">Assembled account</span>
              <h2>{context.account.name}</h2>
              <p>{context.account.industry} · {context.account.segment} · Owner {context.account.owner_name ?? 'Unassigned'}</p>
              <div className="brief-facts">
                <div><span>Account value</span><strong>{formatCurrency(context.account.account_value)}</strong></div>
                <div><span>Opportunity</span><strong>{formatCurrency(context.opportunity?.amount)}</strong></div>
                <div><span>Open order value</span><strong>{formatCurrency(openOrderValue)}</strong></div>
              </div>
            </article>
            <article className="decision-readiness">
              <div className="readiness-header">
                <span className="kicker">Decision readiness</span>
                <StatusPill label={context.context_completeness} tone={completenessTone} />
              </div>
              <div className="readiness-metrics">
                <div>
                  <span>Risk tier</span>
                  <strong>{renewalSignal?.risk_tier?.toUpperCase() ?? 'UNKNOWN'}</strong>
                  <StatusPill label={renewalSignal?.risk_tier ?? 'unknown'} tone={riskTone} />
                </div>
                <div>
                  <span>ARR</span>
                  <strong>{formatCurrency(subscription?.arr)}</strong>
                  <small>Subscription annual recurring revenue</small>
                </div>
                <div>
                  <span>Usage health</span>
                  <strong>{percent(subscription?.usage_health_score)}</strong>
                  <small>{subscription?.usage_trend ?? 'Unknown trend'}</small>
                </div>
                <div>
                  <span>Recommended action</span>
                  <strong>{labelFromRule(renewalSignal?.recommended_action ?? 'pending')}</strong>
                  <small>{subscription?.days_to_renewal ?? '-'} days to renewal</small>
                </div>
              </div>
            </article>
          </section>

          <section className="source-evidence-panel">
            <div className="section-heading">
              <span className="kicker">Source stack</span>
              <h2>Systems that contributed to this UnifiedContext</h2>
              <p>{context.missing_sources.length ? `Missing sources: ${context.missing_sources.join(', ')}` : 'All active source systems responded for this context run.'}</p>
            </div>
            <div className="source-evidence-strip">
              {sourceStack.map(([slot, provider]) => (
                <article key={slot}>
                  <span>{slot}</span>
                  <strong>{provider}</strong>
                </article>
              ))}
            </div>
          </section>

          <section className="context-operating-grid">
            <article className="business-card context-panel">
              <div className="card-title-row">
                <h3>Renewal Posture</h3>
                <StatusPill label={renewalSignal?.risk_tier ?? 'unknown'} tone={riskTone} />
              </div>
              <dl className="detail-list">
                <div><dt>Renewal date</dt><dd>{subscription?.renewal_date}</dd></div>
                <div><dt>Days to renewal</dt><dd>{subscription?.days_to_renewal}</dd></div>
                <div><dt>Escalations</dt><dd>{subscription?.escalation_count_90d}</dd></div>
                <div><dt>Recommended action</dt><dd>{labelFromRule(renewalSignal?.recommended_action ?? 'pending')}</dd></div>
              </dl>
            </article>
            <article className="business-card context-panel">
              <h3>Opportunity & Orders</h3>
              <dl className="detail-list">
                <div><dt>Opportunity</dt><dd>{context.opportunity?.name ?? 'No active opportunity'}</dd></div>
                <div><dt>Stage</dt><dd>{labelFromRule(context.opportunity?.stage ?? 'unknown')}</dd></div>
                <div><dt>Probability</dt><dd>{percent(context.opportunity?.probability)}</dd></div>
                <div><dt>Orders</dt><dd>{context.orders.length} records · {formatCurrency(openOrderValue)}</dd></div>
              </dl>
            </article>
            <article className="business-card context-panel">
              <h3>Expansion Signal</h3>
              <dl className="detail-list">
                <div><dt>Upsell propensity</dt><dd>{percent(renewalSignal?.upsell_propensity)}</dd></div>
                <div><dt>Expansion products</dt><dd>{renewalSignal?.expansion_products?.length ?? 0}</dd></div>
                <div><dt>Churn indicators</dt><dd>{renewalSignal?.churn_indicators?.length ?? 0}</dd></div>
              </dl>
            </article>
          </section>

          <section className="context-evidence-grid">
            <article className="business-card context-panel">
              <h3>Installed Products</h3>
              {installedProducts.map((product) => (
                <div className="row-item" key={product.product_id}>
                  <strong>{product.product_name}</strong>
                  <span>{product.quantity} · {product.support_level ?? 'standard'} · {product.location ?? 'no location'}</span>
                </div>
              ))}
            </article>
            <article className="business-card context-panel">
              <h3>Recent Activity</h3>
              {context.activities.slice(0, 4).map((activity) => (
                <div className="row-item" key={activity.activity_id}>
                  <strong>{activity.subject}</strong>
                  <span>{activity.activity_type} · {activity.sentiment}</span>
                </div>
              ))}
            </article>
            <article className="business-card context-panel">
              <h3>Conflict Handling</h3>
              {context.conflict_resolutions.map((item) => (
                <div className="row-item" key={`${item.field_path}-${item.rule_applied}`}>
                  <strong>{labelFromPath(item.field_path)}</strong>
                  <span>{labelFromRule(item.rule_applied)} · {labelFromRule(item.winning_source)}</span>
                </div>
              ))}
            </article>
          </section>

          <section className="context-next-step">
            <div>
              <span className="kicker">Next step</span>
              <h2>Send this assembled context to Decision Cockpit</h2>
              <p>The DecisionAgent will price the renewal using the same normalized facts shown here, then write the rationale to Audit Trail.</p>
            </div>
            <div className="button-row">
              <button className="primary-action" onClick={() => requestDecisionRun?.() ?? goTo('decision')}>Run Decision in Cockpit</button>
              <button className="secondary-action" onClick={() => goTo('stack')}>Review Vendor Stack</button>
            </div>
          </section>
          <EvidenceDrawer title="Raw UnifiedContext" data={context} />
        </>
      )}
    </div>
  );
}
