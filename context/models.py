from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=False)


class CRMProvider(str, Enum):
    SALESFORCE = "salesforce"
    DYNAMICS = "dynamics"
    ORACLE_CRM = "oracle_crm"


class OMSProvider(str, Enum):
    ORACLE_FOM = "oracle_fom"
    SALESFORCE_OMS = "salesforce_oms"
    SAP_S4HANA = "sap_s4hana"
    ZUORA_OMS = "zuora_oms"
    NETSUITE = "netsuite"


class SubProvider(str, Enum):
    ORACLE_SUBSCRIPTION = "oracle_subscription"
    ZUORA_SUB = "zuora_sub"
    CHARGEBEE = "chargebee"
    SALESFORCE_REVENUE = "salesforce_revenue"


class InstallBaseProvider(str, Enum):
    ORACLE_INSTALL_BASE = "oracle_install_base"
    SALESFORCE_ASSET = "salesforce_asset"
    SERVICENOW_CMDB = "servicenow_cmdb"


class AppMode(str, Enum):
    DEMO = "demo"
    REAL = "real"


class Segment(str, Enum):
    ENTERPRISE = "enterprise"
    MID_MARKET = "mid_market"
    SMB = "smb"


class OpportunityType(str, Enum):
    RENEWAL = "renewal"
    NEW_BUSINESS = "new_business"
    EXPANSION = "expansion"


class OpportunityStage(str, Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class ContactRole(str, Enum):
    ECONOMIC_BUYER = "economic_buyer"
    TECHNICAL_EVALUATOR = "technical_evaluator"
    CHAMPION = "champion"
    LEGAL = "legal"
    PROCUREMENT = "procurement"
    OTHER = "other"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PENDING_RENEWAL = "pending_renewal"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class UrgencyTier(str, Enum):
    CRITICAL = "critical"
    URGENT = "urgent"
    NORMAL = "normal"
    EARLY = "early"


class BillingFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class UsageTrend(str, Enum):
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"


class OrderType(str, Enum):
    NEW = "new"
    RENEWAL = "renewal"
    EXPANSION = "expansion"
    CHANGE = "change"


class OrderStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class QuoteStatus(str, Enum):
    DRAFT = "draft"
    PRESENTED = "presented"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ActivityType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    CASE = "case"
    NOTE = "note"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendedAction(str, Enum):
    STANDARD_RENEWAL = "standard_renewal"
    RISK_ADJUSTED_RENEWAL = "risk_adjusted_renewal"
    SAVE_PLAY = "save_play"
    ESCALATE_TO_CSM = "escalate_to_csm"


class Completeness(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    DEGRADED = "degraded"


class InstalledProduct(FrozenModel):
    product_id: str
    product_name: str
    quantity: int
    install_date: date
    location: str | None = None
    support_level: str | None = None
    end_of_support_date: date | None = None


class CanonicalAccount(FrozenModel):
    canonical_account_id: str
    crm_source: CRMProvider
    crm_source_id: str
    name: str
    industry: str
    segment: Segment
    account_value: Decimal
    employee_count: int | None
    region: str
    health_score: float = Field(ge=0.0, le=1.0)
    last_activity_date: datetime | None = None
    owner_name: str | None = None
    installed_base: list[InstalledProduct] | None = None


class CanonicalOpportunity(FrozenModel):
    opportunity_id: str
    account_id: str
    name: str
    opportunity_type: OpportunityType
    stage: OpportunityStage
    amount: Decimal
    close_date: date
    probability: float = Field(ge=0.0, le=1.0)


class CanonicalContact(FrozenModel):
    contact_id: str
    account_id: str
    full_name: str
    email: str
    title: str | None = None
    role: ContactRole = ContactRole.OTHER
    is_primary: bool = False


class CanonicalSubscription(FrozenModel):
    subscription_id: str
    account_id: str
    status: SubscriptionStatus
    start_date: date
    renewal_date: date
    arr: Decimal
    contracted_products: list[str]
    billing_frequency: BillingFrequency
    usage_health_score: float = Field(ge=0.0, le=1.0)
    usage_trend: UsageTrend
    escalation_count_90d: int = Field(ge=0)
    last_expansion_date: date | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def days_to_renewal(self) -> int:
        return (self.renewal_date - date.today()).days

    @computed_field  # type: ignore[prop-decorator]
    @property
    def urgency_tier(self) -> UrgencyTier:
        days = self.days_to_renewal
        if days <= 30:
            return UrgencyTier.CRITICAL
        if days <= 60:
            return UrgencyTier.URGENT
        if days <= 120:
            return UrgencyTier.NORMAL
        return UrgencyTier.EARLY


class OrderLineItem(FrozenModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    line_amount: Decimal


class CanonicalOrder(FrozenModel):
    order_id: str
    account_id: str
    order_number: str
    order_type: OrderType
    status: OrderStatus
    ordered_date: date
    total_amount: Decimal
    line_items: list[OrderLineItem]


class QuoteLineItem(FrozenModel):
    product_id: str
    product_name: str
    quantity: int
    list_price: Decimal
    net_price: Decimal


class CanonicalQuote(FrozenModel):
    quote_id: str
    account_id: str
    status: QuoteStatus
    total_list_price: Decimal
    total_net_price: Decimal
    line_items: list[QuoteLineItem]


class PricingTier(FrozenModel):
    segment: Segment
    min_quantity: int
    list_price: Decimal
    discount_pct: float = Field(ge=0.0, le=1.0)


class ConfigRule(FrozenModel):
    rule_id: str
    description: str
    required_product_ids: list[str] = Field(default_factory=list)
    incompatible_product_ids: list[str] = Field(default_factory=list)


class CanonicalProduct(FrozenModel):
    product_id: str
    name: str
    category: str
    is_active: bool
    bundle_eligibility: list[str]
    pricing_tiers: list[PricingTier]
    config_rules: list[ConfigRule] = Field(default_factory=list)


class CanonicalActivity(FrozenModel):
    activity_id: str
    account_id: str
    activity_type: ActivityType
    activity_date: datetime
    subject: str
    description: str
    sentiment: Sentiment


class ChurnIndicator(FrozenModel):
    indicator_type: str
    severity: str
    description: str


class PricingRecommendation(FrozenModel):
    base_price: Decimal
    risk_adjusted_price: Decimal
    max_discount_pct: float
    rationale: str


class RenewalSignal(FrozenModel):
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_tier: RiskTier
    churn_indicators: list[ChurnIndicator]
    upsell_propensity: float = Field(ge=0.0, le=1.0)
    expansion_products: list[str]
    recommended_action: RecommendedAction
    pricing_recommendation: PricingRecommendation | None = None


class SourceAttribution(FrozenModel):
    source: str
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    field_path: str | None = None


class ConflictResolution(FrozenModel):
    field_path: str
    winning_source: str
    losing_sources: list[str]
    rule_applied: str
    chosen_value: Any


class UnifiedContext(FrozenModel):
    context_run_id: str
    assembled_at: datetime
    crm_provider: CRMProvider
    oms_provider: OMSProvider
    sub_provider: SubProvider
    install_base_provider: InstallBaseProvider = InstallBaseProvider.ORACLE_INSTALL_BASE
    account: CanonicalAccount
    opportunity: CanonicalOpportunity | None = None
    contacts: list[CanonicalContact] = Field(default_factory=list)
    subscription: CanonicalSubscription | None = None
    orders: list[CanonicalOrder] = Field(default_factory=list)
    activities: list[CanonicalActivity] = Field(default_factory=list)
    products: list[CanonicalProduct] = Field(default_factory=list)
    renewal_signal: RenewalSignal | None = None
    source_attribution: dict[str, SourceAttribution] = Field(default_factory=dict)
    conflict_resolutions: list[ConflictResolution] = Field(default_factory=list)
    context_completeness: Completeness
    missing_sources: list[str] = Field(default_factory=list)
