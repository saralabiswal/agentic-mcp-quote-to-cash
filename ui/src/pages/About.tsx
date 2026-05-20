/* Author: Sarala Biswal */
import { PageId, Scenario } from '../App';
import { IconFor, MetricCard, PageHeader, StoryStep } from '../components/Presentation';

type Props = {
  scenario: Scenario;
  goTo: (page: PageId) => void;
};

export default function Overview({ scenario, goTo }: Props) {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Executive Narrative"
        title="Quote-to-cash agentic decision flow"
        subtitle="A live MCP integration layer assembles customer truth from enterprise systems, then produces a deterministic renewal decision with full audit evidence."
      >
        <button className="primary-action" onClick={() => goTo('scenarios')}>Start with Demo Scenarios</button>
      </PageHeader>

      <section className="executive-overview">
        <article className="executive-problem">
          <span className="kicker">Business Problem</span>
          <h2>Renewal agents need live commercial context, not yesterday&apos;s CRM snapshot.</h2>
          <p>
            CRM, CPQ, Order Management Systems, subscription, and install-base systems each hold part of the renewal truth.
            This app shows how MCP adapters assemble those signals into one governed context before
            the agent calculates risk, price, and action.
          </p>
          <div className="executive-points">
            <div><strong>Fragmented data</strong><span>Customer, quote, order, usage, and entitlement facts live in separate systems.</span></div>
            <div><strong>Revenue risk</strong><span>Stale snapshots miss usage decline, escalations, order changes, and renewal urgency.</span></div>
            <div><strong>Agentic decision</strong><span>UnifiedContext drives deterministic pricing, rationale, and audit evidence.</span></div>
          </div>
        </article>

        <aside className="scenario-summary">
          <div className="summary-title">
            <IconFor name="decision" />
            <div>
              <span className="kicker">Active Scenario</span>
              <h3>{scenario.name}</h3>
            </div>
          </div>
          <dl>
            <div><dt>Account</dt><dd>{scenario.accountId}</dd></div>
            <div><dt>Runtime stack</dt><dd>{scenario.stack}</dd></div>
            <div><dt>Expected decision</dt><dd>{scenario.expected}</dd></div>
          </dl>
          <button className="secondary-action" onClick={() => goTo('scenarios')}>Choose Scenario</button>
        </aside>
      </section>

      <section className="operating-model">
        <div className="section-heading">
          <span className="kicker">Operating Model</span>
          <h2>From fragmented source systems to governed renewal action</h2>
          <p>
            The story is intentionally simple: connect systems by configuration, normalize the
            commercial facts, run the decision policy, and keep the proof.
          </p>
        </div>
        <div className="model-steps">
          <StoryStep
            index={1}
            title="Collect"
            body="MCP adapters pull CRM, CPQ, Order Management Systems, subscription, and install-base records."
            tone="danger"
          />
          <StoryStep
            index={2}
            title="Normalize"
            body="Vendor payloads map into identical canonical objects and conflict rules."
            tone="good"
          />
          <StoryStep
            index={3}
            title="Decide"
            body="The agent calculates risk, renewal action, price, approval posture, and rationale."
          />
          <StoryStep
            index={4}
            title="Audit"
            body="Every run stores source attribution, context completeness, and reasoning trace."
          />
        </div>
      </section>

      <section className="metric-grid">
        <MetricCard label="Adapters" value="16" detail="CRM, CPQ, Order Management Systems, subscription, install base" tone="good" />
        <MetricCard label="Agent code changes" value="0" detail="Vendor swap happens through runtime settings" tone="good" />
        <MetricCard label="Decision path" value="Deterministic" detail="No LLM in pricing or risk calculation" />
        <MetricCard label="Auditability" value="Full" detail="Context run, decision run, conflicts, and source attribution" />
      </section>

      <section className="risk-comparison">
        <article className="narrative-card danger">
          <h3>Without live context</h3>
          <p>
            The agent sees a healthy CRM snapshot, recommends full-price renewal, and misses recent
            support escalations plus declining subscription usage.
          </p>
          <div className="business-impact">Revenue leakage and late-cycle escalation.</div>
        </article>
        <article className="narrative-card good">
          <h3>With MCP-assembled context</h3>
          <p>
            The agent sees the account, opportunity, orders, subscription health, install base, and
            activity sentiment in one unified context.
          </p>
          <div className="business-impact">Risk-adjusted offer with a defensible audit trail.</div>
        </article>
      </section>
    </div>
  );
}
