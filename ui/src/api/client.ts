/* Author: Sarala Biswal */
/* Code documentation: Typed API client for settings, readiness, context assembly, decision runs, audit history, and demos. */
const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

export type StackSettings = {
  crm_provider: 'salesforce' | 'dynamics' | 'oracle_crm';
  oms_provider: 'oracle_fom' | 'salesforce_oms' | 'sap_s4hana' | 'zuora_oms' | 'netsuite';
  sub_provider: 'oracle_subscription' | 'zuora_sub' | 'chargebee' | 'salesforce_revenue';
  install_base_provider: 'oracle_install_base' | 'salesforce_asset' | 'servicenow_cmdb';
  install_base_enabled: boolean;
};

export type Readiness = {
  name: string;
  provider: string;
  mode: string;
  status: 'green' | 'yellow' | 'red';
  latency_ms: number;
};

export type InstalledProduct = {
  product_id: string;
  product_name: string;
  quantity: number;
  location?: string;
  support_level?: string;
};

export type UnifiedContext = {
  context_run_id: string;
  context_completeness: string;
  crm_provider: string;
  oms_provider: string;
  sub_provider: string;
  install_base_provider?: string;
  account: {
    canonical_account_id: string;
    name: string;
    segment: string;
    industry: string;
    account_value: string;
    health_score: number;
    owner_name?: string;
    installed_base?: InstalledProduct[];
  };
  opportunity?: {
    name: string;
    stage: string;
    amount: string;
    close_date: string;
    probability: number;
  };
  subscription?: {
    subscription_id: string;
    status: string;
    renewal_date: string;
    arr: string;
    usage_health_score: number;
    usage_trend: string;
    escalation_count_90d: number;
    days_to_renewal: number;
    urgency_tier: string;
    contracted_products: string[];
  };
  orders: Array<{ order_id: string; order_type: string; status: string; total_amount: string }>;
  activities: Array<{ activity_id: string; subject: string; sentiment: string; activity_type: string }>;
  renewal_signal?: {
    risk_tier: string;
    recommended_action: string;
    risk_score: number;
    upsell_propensity: number;
    churn_indicators: Array<{ indicator_type: string; severity: string; description: string }>;
    expansion_products: string[];
  };
  missing_sources: string[];
  conflict_resolutions: Array<{ field_path: string; rule_applied: string; winning_source: string }>;
};

export type AgentDecision = {
  context_run_id: string;
  account_id: string;
  created_at: string;
  risk_score?: number;
  risk_tier: string;
  recommended_action: string;
  base_price?: string;
  adjusted_price: string;
  decision_flag: string;
  reasoning_steps: string[];
  approval_required: boolean;
  discount_pct: number;
  margin_pct?: number;
  confidence: string;
  expansion_offer?: { product_id: string; product_name: string; expansion_price: string; rationale: string };
};

export type DemoResult = {
  scenario: number;
  account_id: string;
  context_completeness: string;
  risk_tier: string;
  recommended_action: string;
  adjusted_price: string;
  decision_flag: string;
  snapshot_vs_live?: {
    snapshot: { risk_tier: string; recommended_action: string };
    live: { risk_tier: string; recommended_action: string };
  };
};

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}
