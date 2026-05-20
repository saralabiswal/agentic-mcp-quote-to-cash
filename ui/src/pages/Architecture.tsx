/* Author: Sarala Biswal */
import { PageId } from '../App';
import { PageHeader, StatusPill } from '../components/Presentation';

const runtimeStages = [
  {
    label: 'Source Systems',
    title: 'Enterprise records',
    body: 'CRM, CPQ, Order Management Systems, Subscription, and Install Base each own part of the commercial truth.',
    facts: ['Salesforce', 'Dynamics', 'Oracle', 'SAP', 'Zuora', 'NetSuite', 'Chargebee', 'ServiceNow'],
  },
  {
    label: 'MCP Layer',
    title: 'Adapter contract',
    body: 'Each adapter handles vendor API shape, credentials, timeout behavior, and source attribution.',
    facts: ['16 adapters', 'demo and real paths', 'readiness checks'],
  },
  {
    label: 'Canonical Layer',
    title: 'UnifiedContext',
    body: 'Vendor payloads normalize into the same frozen business objects before any agent logic runs.',
    facts: ['Account', 'Orders', 'Subscription', 'Installed products', 'Activities'],
  },
  {
    label: 'Decision Support',
    title: 'Auditable action',
    body: 'The DecisionAgent calculates risk, price, approval posture, and rationale from canonical facts only.',
    facts: ['Risk tier', 'Adjusted price', 'Approval', 'Evidence'],
  },
];

const proofPoints = [
  {
    label: 'Vendor isolation',
    title: 'DecisionAgent never imports adapters.',
    body: 'Switching Salesforce to Dynamics or Oracle FOM to Zuora changes configuration and source attribution, not decision code.',
  },
  {
    label: 'Resilience',
    title: 'Partial context stays usable.',
    body: 'Timeouts become missing-source evidence and completeness indicators, so the demo can still explain degraded decisions.',
  },
  {
    label: 'Commercial proof',
    title: 'Same facts, same decision.',
    body: 'Equivalent account data across vendors becomes the same canonical context and produces the same business result.',
  },
];

const adapterSlots = [
  {
    slot: 'CRM',
    role: 'Customer, opportunity, contacts, relationship owner, activity sentiment',
    canonical: ['Account', 'Opportunity', 'Contact', 'Activity'],
    adapters: ['Salesforce CRM', 'MS Dynamics 365', 'Oracle CX Sales'],
  },
  {
    slot: 'CPQ',
    role: 'Quote baseline, product catalog, list price, margin guardrails',
    canonical: ['Quote', 'Product', 'PriceBook'],
    adapters: ['Oracle CPQ Cloud'],
  },
  {
    slot: 'Order Management Systems',
    role: 'Open orders, fulfillment status, delivery risk, order value',
    canonical: ['Order', 'OrderLine', 'FulfillmentStatus'],
    adapters: ['Oracle FOM', 'Salesforce Order Management', 'SAP S/4HANA', 'Zuora Order Management', 'NetSuite Order Management'],
  },
  {
    slot: 'Subscription',
    role: 'ARR, renewal date, usage health, escalation posture',
    canonical: ['Subscription', 'UsageHealth', 'RenewalSignal'],
    adapters: ['Oracle Sub Cloud', 'Zuora Sub', 'Chargebee', 'Salesforce Revenue Cloud'],
  },
  {
    slot: 'Install Base',
    role: 'Installed products, entitlement, quantity, location, support coverage',
    canonical: ['InstalledProduct', 'Entitlement'],
    adapters: ['Oracle Install Base', 'Salesforce Asset Management', 'ServiceNow CMDB'],
  },
];

type Props = {
  goTo: (page: PageId) => void;
};

export default function Architecture({ goTo }: Props) {
  return (
    <div className="page-stack architecture-page">
      <PageHeader
        eyebrow="Architecture Proof"
        title="Vendor systems change. The decision contract does not."
        subtitle="A config-driven MCP layer converts fragmented commercial records into one canonical context for deterministic, auditable quote-to-cash decisions."
      >
        <button className="primary-action" onClick={() => goTo('scenarios')}>Run Another Scenario</button>
        <button className="secondary-action" onClick={() => goTo('stack')}>Review Vendor Stack</button>
      </PageHeader>

      <section className="architecture-runtime">
        {runtimeStages.map((stage, index) => (
          <article className="runtime-stage" key={stage.label}>
            <div className="stage-index">{String(index + 1).padStart(2, '0')}</div>
            <span>{stage.label}</span>
            <h3>{stage.title}</h3>
            <p>{stage.body}</p>
            <div className="stage-facts">
              {stage.facts.map((fact) => <strong key={fact}>{fact}</strong>)}
            </div>
          </article>
        ))}
      </section>

      <section className="architecture-proof">
        {proofPoints.map((point) => (
          <article className="proof-card" key={point.label}>
            <span>{point.label}</span>
            <h3>{point.title}</h3>
            <p>{point.body}</p>
          </article>
        ))}
      </section>

      <section className="canonical-panel">
        <div>
          <span className="kicker">Canonical Contract</span>
          <h2>Every adapter must land on the same business language.</h2>
          <p>
            The UI can switch vendors freely because the agent never reasons over vendor payloads.
            It reasons over account health, subscription posture, order state, installed products,
            activity sentiment, pricing guardrails, and audit evidence.
          </p>
        </div>
        <div className="contract-metrics">
          <article><span>Adapters</span><strong>16</strong></article>
          <article><span>Agent rewrites</span><strong>0</strong></article>
          <article><span>Decision path</span><strong>Deterministic</strong></article>
          <article><span>Evidence</span><strong>Audited</strong></article>
        </div>
      </section>

      <section className="adapter-topology">
        <div className="section-heading">
          <span className="kicker">Adapter Slots</span>
          <h2>One slot can have many vendors, but one canonical output contract.</h2>
        </div>

        {adapterSlots.map((slot) => (
          <article className="adapter-slot-row" key={slot.slot}>
            <div className="slot-heading">
              <h3>{slot.slot}</h3>
              <StatusPill label={`${slot.adapters.length} option${slot.adapters.length === 1 ? '' : 's'}`} />
            </div>
            <p>{slot.role}</p>
            <div className="slot-canonical">
              {slot.canonical.map((item) => <strong key={item}>{item}</strong>)}
            </div>
            <div className="slot-adapters">
              {slot.adapters.map((adapter) => <span key={adapter}>{adapter}</span>)}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
