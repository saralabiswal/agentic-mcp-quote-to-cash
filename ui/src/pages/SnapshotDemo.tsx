/* Author: Sarala Biswal */
import { useEffect, useState } from 'react';
import { PageId, Scenario } from '../App';
import { AgentDecision, apiPost, DemoResult } from '../api/client';
import { EvidenceDrawer, formatCurrency, MetricCard, PageHeader, StatusPill } from '../components/Presentation';

type Props = {
  scenario: Scenario;
  goTo: (page: PageId) => void;
  decisionRunRequest?: number;
};

const displayReasoning = (step: string) =>
  step
    .replace(/\bOMS\b/g, 'Order Management Systems')
    .replace(/\bSub\b/g, 'Subscription')
    .replace(/Decision flag: none/g, 'Decision flag: No blocking flag')
    .replace(/zuora_oms/g, 'Zuora Order Management')
    .replace(/salesforce_oms/g, 'Salesforce Order Management')
    .replace(/oracle_fom/g, 'Oracle FOM')
    .replace(/sap_s4hana/g, 'SAP S/4HANA')
    .replace(/netsuite/g, 'NetSuite Order Management')
    .replace(/oracle_subscription/g, 'Oracle Sub Cloud')
    .replace(/zuora_sub/g, 'Zuora Sub')
    .replace(/salesforce_revenue/g, 'Salesforce Revenue Cloud');

const decisionFlagLabel = (flag: string) => {
  const labels: Record<string, string> = {
    none: 'No blocking flag',
    requires_human_review: 'Human review required',
    proposal_locked: 'Proposal locked',
  };
  return labels[flag] ?? flag.replace(/_/g, ' ');
};

export default function DecisionCockpit({ scenario, goTo, decisionRunRequest = 0 }: Props) {
  const [demo, setDemo] = useState<DemoResult | null>(null);
  const [decision, setDecision] = useState<AgentDecision | null>(null);
  const [loading, setLoading] = useState(false);

  async function runDecision() {
    setLoading(true);
    try {
      const [demoResult, decisionResult] = await Promise.all([
        apiPost<DemoResult>(`/demo/${scenario.id}`, {}),
        apiPost<AgentDecision>('/agent/run', { account_id: scenario.accountId }),
      ]);
      setDemo(demoResult);
      setDecision(decisionResult);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (decisionRunRequest > 0) {
      void runDecision();
    }
  }, [decisionRunRequest]);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Decision Cockpit"
        title="Risk, price, and action in one auditable view"
        subtitle="The decision agent turns unified context into a renewal action, adjusted price, approval posture, and reasoning trace."
      >
        <button className="primary-action" onClick={runDecision} disabled={loading}>
          {loading ? 'Running...' : decision ? 'Re-run Decision' : 'Run Decision'}
        </button>
      </PageHeader>

      <section className="decision-panel">
        <div>
          <span className="kicker">Current story</span>
          <h2>{scenario.name}</h2>
          <p>{scenario.accountId} · {scenario.stack}</p>
        </div>
        <StatusPill label={scenario.expected} tone="good" />
      </section>

      <section className="business-card proof-note">
        <span className="kicker">How to read vendor swaps</span>
        <p>
          Vendor changes are not supposed to create a new commercial answer by themselves. They prove
          that equivalent source records normalize into the same UnifiedContext. The decision changes
          only when the underlying account facts change, such as usage health, escalations, order
          state, subscription posture, or missing sources.
        </p>
      </section>

      {demo?.snapshot_vs_live ? (
        <section className="two-column">
          <article className="narrative-card danger">
            <h3>Snapshot Decision</h3>
            <p>Risk tier: {demo.snapshot_vs_live.snapshot.risk_tier}</p>
            <strong>{demo.snapshot_vs_live.snapshot.recommended_action}</strong>
          </article>
          <article className="narrative-card good">
            <h3>Live MCP Decision</h3>
            <p>Risk tier: {demo.snapshot_vs_live.live.risk_tier}</p>
            <strong>{demo.snapshot_vs_live.live.recommended_action}</strong>
          </article>
        </section>
      ) : null}

      {decision ? (
        <>
          <section className="metric-grid">
            <MetricCard label="Risk Tier" value={decision.risk_tier.toUpperCase()} detail="Calculated from usage, escalations, urgency, and sentiment" tone={decision.risk_tier === 'critical' || decision.risk_tier === 'high' ? 'danger' : 'good'} />
            <MetricCard label="Adjusted Price" value={formatCurrency(decision.adjusted_price)} detail={`Discount ${Math.round(decision.discount_pct * 100)}%`} />
            <MetricCard label="Action" value={decision.recommended_action} detail={decisionFlagLabel(decision.decision_flag)} tone={decision.decision_flag === 'none' ? 'good' : 'warn'} />
            <MetricCard label="Approval" value={decision.approval_required ? 'Required' : 'Not required'} detail={`Confidence: ${decision.confidence}`} tone={decision.approval_required ? 'warn' : 'good'} />
          </section>

          <section className="business-card">
            <div className="card-title-row">
              <h3>Reasoning Trace</h3>
              <button className="secondary-action" onClick={() => goTo('audit')}>View Audit Evidence</button>
            </div>
            <div className="timeline">
              {decision.reasoning_steps.map((step, index) => (
                <div className="timeline-item" key={step}>
                  <span>{index + 1}</span>
                  <p>{displayReasoning(step)}</p>
                </div>
              ))}
            </div>
          </section>

          <EvidenceDrawer title="Decision Payload" data={{ demo, decision }} />
        </>
      ) : (
        <section className="empty-state">
          <h2>Run the decision to reveal the business outcome</h2>
          <p>The default story starts with TechCorp and shows why stale snapshots produce different risk posture.</p>
        </section>
      )}
    </div>
  );
}
