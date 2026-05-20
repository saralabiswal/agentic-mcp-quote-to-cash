/* Author: Sarala Biswal */
import { useMemo, useState } from 'react';
import {
  Activity,
  BarChart3,
  FileSearch,
  GitBranch,
  Layers3,
  Network,
  Presentation,
  Workflow,
} from 'lucide-react';
import Architecture from './pages/Architecture';
import AuditTrail from './pages/AgentRuns';
import DecisionCockpit from './pages/SnapshotDemo';
import LiveContext from './pages/ContextExplorer';
import LogicalArchitecture from './pages/LogicalArchitecture';
import Overview from './pages/About';
import ScenarioWalkthrough from './pages/StackConfigurator';

export type Scenario = {
  id: number;
  accountId: string;
  name: string;
  stack: string;
  expected: string;
  pattern: string;
};

const scenarios: Scenario[] = [
  {
    id: 1,
    accountId: 'ACC-001',
    name: 'TechCorp Snapshot vs Live',
    stack: 'Salesforce + Oracle FOM + Oracle Sub',
    expected: 'Live HIGH risk, risk-adjusted renewal at $79,500',
    pattern: 'High risk with expansion offer',
  },
  {
    id: 2,
    accountId: 'ACC-002',
    name: 'GlobalBanking Happy Path',
    stack: 'Salesforce + Oracle FOM + Oracle Sub',
    expected: 'LOW risk, standard renewal with expansion offer',
    pattern: 'Healthy renewal and expansion',
  },
  {
    id: 3,
    accountId: 'ACC-002',
    name: 'CRM Vendor Swap',
    stack: 'Dynamics + Oracle FOM + Oracle Sub',
    expected: 'Same decision as Scenario 2 with zero agent changes',
    pattern: 'Vendor swap, same facts',
  },
  {
    id: 4,
    accountId: 'ACC-003',
    name: 'Non-Salesforce Stack',
    stack: 'Oracle CRM + SAP Order Management Systems + Zuora Sub',
    expected: 'CRITICAL risk, escalate to CSM',
    pattern: 'Critical escalation',
  },
  {
    id: 5,
    accountId: 'ACC-001',
    name: 'Mixed Vendor Stack',
    stack: 'Salesforce + Zuora Order Management Systems + Chargebee',
    expected: 'HIGH risk, risk-adjusted renewal',
    pattern: 'Mixed systems, same account risk',
  },
  {
    id: 6,
    accountId: 'ACC-003',
    name: 'Degraded Context',
    stack: 'Salesforce + Oracle FOM + simulated Sub timeout',
    expected: 'PARTIAL context, human review required',
    pattern: 'Partial context governance',
  },
  {
    id: 7,
    accountId: 'ACC-004',
    name: 'RetailCo Save Play',
    stack: 'Salesforce + Oracle FOM + Oracle Sub',
    expected: 'HIGH risk, low upsell fit, save play motion',
    pattern: 'Save play without expansion',
  },
];

const pages = [
  { id: 'overview', label: 'Overview', stage: '01', outcome: 'Frame the business risk', icon: Presentation, component: Overview },
  { id: 'scenarios', label: 'Demo Scenarios', stage: '02', outcome: 'Pick the renewal story', icon: BarChart3, component: ScenarioWalkthrough },
  { id: 'stack', label: 'Vendor Stack', stage: '03', outcome: 'Switch systems by config', icon: Network, component: ScenarioWalkthrough },
  { id: 'context', label: 'Live Context', stage: '04', outcome: 'Assemble customer truth', icon: Activity, component: LiveContext },
  { id: 'decision', label: 'Decision Cockpit', stage: '05', outcome: 'Price with guardrails', icon: GitBranch, component: DecisionCockpit },
  { id: 'audit', label: 'Audit Trail', stage: '06', outcome: 'Prove every decision', icon: FileSearch, component: AuditTrail },
  { id: 'architecture', label: 'Architecture', stage: '07', outcome: 'Show the platform pattern', icon: Layers3, component: Architecture },
  { id: 'logical-architecture', label: 'Logical Architecture', stage: '08', outcome: 'Map the runtime flow', icon: Workflow, component: LogicalArchitecture },
] as const;

export type PageId = (typeof pages)[number]['id'];

export default function App() {
  const [active, setActive] = useState<PageId>('overview');
  const [scenarioId, setScenarioId] = useState(1);
  const [decisionRunRequest, setDecisionRunRequest] = useState(0);
  const activeScenario = useMemo(
    () => scenarios.find((scenario) => scenario.id === scenarioId) ?? scenarios[0],
    [scenarioId],
  );
  const Page = pages.find((page) => page.id === active)?.component ?? Overview;

  function openDecisionAndRun() {
    setDecisionRunRequest((value) => value + 1);
    setActive('decision');
  }

  return (
    <div className="app-shell">
      <aside className="side-nav">
        <div className="brand-block">
          <span className="brand-mark">Q2C</span>
          <div>
            <strong>Quote-to-Cash MCP</strong>
            <small>Live commercial context</small>
            <small className="author-line">Author: Sarala Biswal</small>
          </div>
        </div>

        <div className="scenario-mini">
          <span>Active Story</span>
          <strong>{activeScenario.name}</strong>
          <small>{activeScenario.expected}</small>
        </div>

        <nav>
          {pages.map((page) => {
            const Icon = page.icon;
            return (
              <button
                key={page.id}
                className={active === page.id ? 'active' : ''}
                onClick={() => setActive(page.id)}
              >
                <Icon size={18} />
                <span>
                  <strong>{page.label}</strong>
                  <small>{page.stage} · {page.outcome}</small>
                </span>
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="content-shell">
        <div className="workspace-topbar">
          <div>
            <span>Decision Support</span>
            <strong>{activeScenario.name}</strong>
          </div>
          <div className="topbar-badges">
            <small>APP_MODE demo</small>
            <small>16 adapters</small>
            <small>Audit ready</small>
          </div>
        </div>
        <Page
          activePage={active}
          scenario={activeScenario}
          scenarios={scenarios}
          setScenarioId={setScenarioId}
          goTo={setActive}
          requestDecisionRun={openDecisionAndRun}
          decisionRunRequest={decisionRunRequest}
        />
      </main>
    </div>
  );
}
