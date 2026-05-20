import { useEffect, useMemo, useState } from 'react';
import { PageId, Scenario } from '../App';
import { AgentDecision, apiGet, apiPost } from '../api/client';
import { EvidenceDrawer, formatCurrency, PageHeader, StatusPill } from '../components/Presentation';

type Props = {
  scenario: Scenario;
  goTo: (page: PageId) => void;
};

type AuditGroup = {
  key: string;
  latest: AgentDecision;
  runs: AgentDecision[];
  sourceVariants: string[];
};

function decisionKey(run: AgentDecision) {
  return [
    run.account_id,
    run.risk_tier,
    run.recommended_action,
    run.adjusted_price,
    run.decision_flag,
    run.confidence,
  ].join('|');
}

function sourceVariant(run: AgentDecision) {
  return run.reasoning_steps.find((step) => step.startsWith('Context: '))?.replace('Context: ', '') ?? 'source attribution unavailable';
}

function groupRuns(runs: AgentDecision[]): AuditGroup[] {
  const byDecision = new Map<string, AuditGroup>();
  runs.forEach((run) => {
    const key = decisionKey(run);
    const existing = byDecision.get(key);
    if (existing) {
      existing.runs.push(run);
      existing.sourceVariants = Array.from(new Set([...existing.sourceVariants, sourceVariant(run)]));
      return;
    }
    byDecision.set(key, {
      key,
      latest: run,
      runs: [run],
      sourceVariants: [sourceVariant(run)],
    });
  });
  return Array.from(byDecision.values());
}

function formatDateTime(value?: string) {
  if (!value) return 'Time unavailable';
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

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

export default function AuditTrail({ scenario, goTo }: Props) {
  const [runs, setRuns] = useState<AgentDecision[]>([]);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [captureLoading, setCaptureLoading] = useState(false);
  const groups = useMemo(() => groupRuns(runs), [runs]);
  const selectedGroup = groups.find((group) => group.key === selectedKey) ?? groups[0] ?? null;
  const selected = selectedGroup?.latest ?? null;

  async function refresh() {
    const data = await apiGet<AgentDecision[]>('/agent/runs');
    setRuns(data);
    setSelectedKey(data[0] ? decisionKey(data[0]) : null);
  }

  async function runAndRefresh() {
    setCaptureLoading(true);
    try {
      await apiPost<AgentDecision>('/agent/run', { account_id: scenario.accountId });
      await refresh();
    } finally {
      setCaptureLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Audit Trail"
        title="Enterprise proof for every renewal recommendation"
        subtitle="Repeated identical executions are grouped into one business decision, while every stored run remains available as evidence."
      >
        <button className="primary-action" onClick={runAndRefresh} disabled={captureLoading}>
          {captureLoading ? 'Capturing...' : 'Capture Current Scenario'}
        </button>
        <button className="secondary-action" onClick={() => goTo('architecture')}>Review Architecture</button>
      </PageHeader>

      <section className="audit-layout">
        <aside className="run-list">
          <div className="card-title-row">
            <h3>Decision History</h3>
            <StatusPill label={`${runs.length} stored`} />
          </div>
          <p className="muted-copy">{groups.length} unique business decision{groups.length === 1 ? '' : 's'}.</p>
          {groups.length === 0 ? <p>No agent runs captured yet.</p> : null}
          {groups.map((group) => (
            <button
              className={selectedGroup?.key === group.key ? 'selected' : ''}
              key={group.key}
              onClick={() => setSelectedKey(group.key)}
            >
              <span>{group.latest.account_id}</span>
              <strong>{group.latest.risk_tier} · {formatCurrency(group.latest.adjusted_price)}</strong>
              <small>{group.latest.recommended_action}</small>
              <em>{group.runs.length} run{group.runs.length === 1 ? '' : 's'} · {group.sourceVariants.length} source path{group.sourceVariants.length === 1 ? '' : 's'}</em>
            </button>
          ))}
        </aside>

        <section className="business-card audit-detail">
          {selected ? (
            <>
              <div className="card-title-row">
                <div>
                  <h3>{selected.account_id}</h3>
                  <p>Latest run: {selected.context_run_id}</p>
                </div>
                <StatusPill label={decisionFlagLabel(selected.decision_flag)} tone={selected.decision_flag === 'none' ? 'good' : 'warn'} />
              </div>
              <section className="audit-summary-band">
                <div>
                  <span>Grouped executions</span>
                  <strong>{selectedGroup?.runs.length ?? 1}</strong>
                </div>
                <div>
                  <span>Latest capture</span>
                  <strong>{formatDateTime(selected.created_at)}</strong>
                </div>
                <div>
                  <span>Source paths</span>
                  <strong>{selectedGroup?.sourceVariants.length ?? 1}</strong>
                </div>
              </section>
              <div className="metric-grid compact-metrics">
                <div><span>Risk</span><strong>{selected.risk_tier}</strong></div>
                <div><span>Price</span><strong>{formatCurrency(selected.adjusted_price)}</strong></div>
                <div><span>Action</span><strong>{selected.recommended_action}</strong></div>
              </div>
              <section className="source-equivalence">
                <h3>Equivalent Source Paths</h3>
                {(selectedGroup?.sourceVariants ?? [sourceVariant(selected)]).map((variant) => (
                  <div className="row-item" key={variant}>
                    <strong>{displayReasoning(variant)}</strong>
                    <span>same canonical decision</span>
                  </div>
                ))}
              </section>
              <div className="timeline">
                {selected.reasoning_steps.map((step, index) => (
                  <div className="timeline-item" key={step}>
                    <span>{index + 1}</span>
                    <p>{displayReasoning(step)}</p>
                  </div>
                ))}
              </div>
              <EvidenceDrawer title="Stored Agent Runs in This Group" data={selectedGroup?.runs ?? [selected]} />
            </>
          ) : (
            <div className="empty-state">
              <h2>Select a run</h2>
              <p>Run the active scenario to create a decision record.</p>
            </div>
          )}
        </section>
      </section>
    </div>
  );
}
