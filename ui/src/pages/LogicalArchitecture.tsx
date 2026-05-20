/* Author: Sarala Biswal */
/* Code documentation: Logical Architecture page that renders the end-to-end runtime diagram. */
import { PageId } from '../App';
import { PageHeader } from '../components/Presentation';

type Props = {
  goTo: (page: PageId) => void;
};

const flowFacts = [
  ['Configuration', 'Vendor choices select adapter implementations at runtime.'],
  ['Canonical contract', 'All vendors land on UnifiedContext before decisioning.'],
  ['Decision support', 'The DecisionAgent consumes business facts, not vendor payloads.'],
  ['Auditability', 'Context, decision, rationale, and source path are stored as evidence.'],
];

export default function LogicalArchitecture({ goTo }: Props) {
  return (
    <div className="page-stack logical-architecture-page">
      <PageHeader
        eyebrow="Logical Architecture"
        title="Quote-to-cash agentic decision flow"
        subtitle="This diagram shows how source systems, MCP adapters, canonical context, decision logic, and audit evidence fit together in the demo application."
      >
        <button className="primary-action" onClick={() => goTo('scenarios')}>Run Demo Scenario</button>
        <button className="secondary-action" onClick={() => goTo('architecture')}>Architecture Story</button>
      </PageHeader>

      <section className="logical-diagram-shell" aria-label="Logical architecture diagram">
        <svg className="logical-diagram" viewBox="0 0 1320 760" role="img" aria-labelledby="logical-title logical-desc">
          <title id="logical-title">Logical architecture for the quote-to-cash agentic decision application</title>
          <desc id="logical-desc">
            Enterprise source systems connect through MCP adapters into a ContextAssembler. The assembler produces UnifiedContext for the DecisionAgent. Decisions and context are stored in audit evidence and surfaced in the React UI.
          </desc>
          <defs>
            <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
              <path d="M0,0 L10,5 L0,10 Z" fill="#2f5f9f" />
            </marker>
            <linearGradient id="nodeBlue" x1="0" x2="1">
              <stop offset="0%" stopColor="#f8fbff" />
              <stop offset="100%" stopColor="#edf5ff" />
            </linearGradient>
            <linearGradient id="nodeGreen" x1="0" x2="1">
              <stop offset="0%" stopColor="#f8fffc" />
              <stop offset="100%" stopColor="#edf9f5" />
            </linearGradient>
            <filter id="softShadow" x="-10%" y="-10%" width="120%" height="130%">
              <feDropShadow dx="0" dy="8" stdDeviation="8" floodColor="#1e293b" floodOpacity="0.10" />
            </filter>
          </defs>

          <rect x="20" y="20" width="1280" height="720" rx="18" fill="#ffffff" stroke="#c6d5e6" />
          <text x="52" y="62" className="svg-title">Logical Architecture</text>
          <text x="52" y="88" className="svg-subtitle">Config-driven MCP integration layer for auditable quote-to-cash decisions</text>

          <g className="svg-zone">
            <rect x="52" y="120" width="250" height="430" rx="14" fill="#f8fafc" stroke="#d2dfeb" />
            <text x="76" y="152" className="svg-zone-title">Enterprise Source Systems</text>
            {[
              ['CRM', 'Salesforce · Dynamics · Oracle CX'],
              ['CPQ', 'Oracle CPQ Cloud'],
              ['Order Management', 'FOM · SF OMS · SAP · Zuora'],
              ['Subscription', 'Oracle Sub · Zuora · Chargebee'],
              ['Install Base', 'Oracle IB · SF Asset · SNOW'],
            ].map(([title, body], index) => (
              <g key={title}>
                <rect x="76" y={178 + index * 68} width="202" height="48" rx="10" fill="#ffffff" stroke="#cbd8e6" />
                <text x="92" y={198 + index * 68} className="svg-node-title">{title}</text>
                <text x="92" y={216 + index * 68} className="svg-node-small">{body}</text>
              </g>
            ))}
          </g>

          <g>
            <rect x="365" y="120" width="210" height="430" rx="14" fill="url(#nodeBlue)" stroke="#bdd0e7" filter="url(#softShadow)" />
            <text x="392" y="152" className="svg-zone-title">MCP Adapter Layer</text>
            <text x="392" y="180" className="svg-node-small">16 adapter implementations</text>
            <text x="392" y="210" className="svg-node-small">mock_call for demo mode</text>
            <text x="392" y="236" className="svg-node-small">real_call stubs or API paths</text>
            <text x="392" y="262" className="svg-node-small">readiness and latency checks</text>
            <text x="392" y="288" className="svg-node-small">source attribution</text>
            <rect x="392" y="328" width="156" height="88" rx="10" fill="#ffffff" stroke="#cbd8e6" />
            <text x="414" y="360" className="svg-node-title">Config selects</text>
            <text x="414" y="382" className="svg-node-small">CRM · OMS · Sub</text>
            <text x="414" y="404" className="svg-node-small">Install Base provider</text>
          </g>

          <g>
            <rect x="660" y="156" width="218" height="112" rx="14" fill="url(#nodeGreen)" stroke="#b9d7cf" filter="url(#softShadow)" />
            <text x="690" y="194" className="svg-node-title">ContextAssembler</text>
            <text x="690" y="220" className="svg-node-small">asyncio.gather</text>
            <text x="690" y="242" className="svg-node-small">return_exceptions=True</text>

            <rect x="660" y="330" width="218" height="112" rx="14" fill="#fffdf7" stroke="#e1d3a8" filter="url(#softShadow)" />
            <text x="690" y="368" className="svg-node-title">Conflict Resolver</text>
            <text x="690" y="394" className="svg-node-small">subscription authoritative</text>
            <text x="690" y="416" className="svg-node-small">install base enrichment</text>
          </g>

          <g>
            <rect x="960" y="174" width="240" height="160" rx="16" fill="#f7fbff" stroke="#b9cde8" filter="url(#softShadow)" />
            <text x="996" y="214" className="svg-node-title">UnifiedContext</text>
            <text x="996" y="240" className="svg-node-small">Account · Opportunity · Contacts</text>
            <text x="996" y="262" className="svg-node-small">Orders · Subscription · Activities</text>
            <text x="996" y="284" className="svg-node-small">Installed products · Products</text>
            <text x="996" y="306" className="svg-node-small">Completeness · Missing sources</text>
          </g>

          <g>
            <rect x="960" y="408" width="240" height="124" rx="16" fill="#f8fff9" stroke="#b8d9c2" filter="url(#softShadow)" />
            <text x="996" y="448" className="svg-node-title">DecisionAgent</text>
            <text x="996" y="474" className="svg-node-small">Risk tier · action · adjusted price</text>
            <text x="996" y="496" className="svg-node-small">Approval posture · decision flag</text>
          </g>

          <g>
            <rect x="660" y="596" width="218" height="92" rx="14" fill="#f8fafc" stroke="#cbd8e6" />
            <text x="690" y="632" className="svg-node-title">Audit Store</text>
            <text x="690" y="658" className="svg-node-small">context run · decision payload</text>
            <text x="690" y="678" className="svg-node-small">reasoning trace · evidence</text>

            <rect x="960" y="596" width="240" height="92" rx="14" fill="#f8fafc" stroke="#cbd8e6" />
            <text x="996" y="632" className="svg-node-title">React Decision Support UI</text>
            <text x="996" y="658" className="svg-node-small">scenario · stack · live context</text>
            <text x="996" y="678" className="svg-node-small">decision cockpit · audit trail</text>
          </g>

          <path className="svg-flow" d="M302 335 H365" />
          <path className="svg-flow" d="M575 255 C615 255 620 212 660 212" />
          <path className="svg-flow" d="M575 394 H660" />
          <path className="svg-flow" d="M878 212 H960" />
          <path className="svg-flow" d="M769 268 V330" />
          <path className="svg-flow" d="M878 386 C920 386 922 254 960 254" />
          <path className="svg-flow" d="M1080 334 V408" />
          <path className="svg-flow" d="M1080 532 C1080 574 878 574 800 596" />
          <path className="svg-flow" d="M878 642 H960" />
          <path className="svg-flow muted" d="M1080 596 C1080 562 1080 562 1080 532" />
          <path className="svg-flow muted" d="M769 596 C730 552 730 492 769 442" />

          <text x="606" y="140" className="svg-flow-label">parallel calls</text>
          <text x="906" y="198" className="svg-flow-label">canonical facts</text>
          <text x="1110" y="378" className="svg-flow-label">decision input</text>
          <text x="810" y="580" className="svg-flow-label">audit evidence</text>
        </svg>
      </section>

      <section className="logical-proof-grid">
        {flowFacts.map(([label, body]) => (
          <article key={label}>
            <span>{label}</span>
            <strong>{body}</strong>
          </article>
        ))}
      </section>
    </div>
  );
}
