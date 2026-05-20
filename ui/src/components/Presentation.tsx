/* Author: Sarala Biswal */
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  CircleDollarSign,
  DatabaseZap,
  FileSearch,
  GitBranch,
  Layers3,
  LockKeyhole,
  Network,
  ShieldCheck,
} from 'lucide-react';
import { ReactNode } from 'react';

export function PageHeader({
  eyebrow,
  title,
  subtitle,
  children,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  children?: ReactNode;
}) {
  return (
    <section className="page-header">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {children ? <div className="header-actions">{children}</div> : null}
    </section>
  );
}

export function MetricCard({
  label,
  value,
  detail,
  tone = 'neutral',
}: {
  label: string;
  value: string;
  detail: string;
  tone?: 'neutral' | 'good' | 'warn' | 'danger';
}) {
  return (
    <article className={`metric-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

export function StatusPill({
  label,
  tone = 'neutral',
}: {
  label: string;
  tone?: 'neutral' | 'good' | 'warn' | 'danger';
}) {
  return <span className={`status-pill ${tone}`}>{label}</span>;
}

export function EvidenceDrawer({ title, data }: { title: string; data: unknown }) {
  return (
    <details className="evidence-drawer">
      <summary>{title}</summary>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </details>
  );
}

export function StoryStep({
  index,
  title,
  body,
  tone = 'neutral',
}: {
  index: number;
  title: string;
  body: string;
  tone?: 'neutral' | 'good' | 'danger';
}) {
  return (
    <div className={`story-step ${tone}`}>
      <span>{index}</span>
      <div>
        <strong>{title}</strong>
        <p>{body}</p>
      </div>
    </div>
  );
}

export function IconFor({ name }: { name: string }) {
  const icons: Record<string, ReactNode> = {
    live: <DatabaseZap size={20} />,
    risk: <AlertTriangle size={20} />,
    decision: <CircleDollarSign size={20} />,
    audit: <FileSearch size={20} />,
    architecture: <Layers3 size={20} />,
    stack: <Network size={20} />,
    branch: <GitBranch size={20} />,
    secure: <ShieldCheck size={20} />,
    lock: <LockKeyhole size={20} />,
    activity: <Activity size={20} />,
    check: <CheckCircle2 size={20} />,
    arrow: <ArrowRight size={20} />,
  };
  return <span className="icon-tile">{icons[name] ?? icons.check}</span>;
}

export const formatCurrency = (value?: string | number) => {
  const parsed = Number(value ?? 0);
  return parsed.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
};

export const percent = (value?: number) => `${Math.round((value ?? 0) * 100)}%`;
