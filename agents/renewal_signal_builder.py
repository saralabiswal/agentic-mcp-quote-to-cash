# Author: Sarala Biswal
"""Renewal signal builder that scores churn risk and expansion readiness from canonical context facts."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from context.models import (
    CanonicalAccount,
    CanonicalActivity,
    CanonicalOrder,
    CanonicalProduct,
    CanonicalSubscription,
    ChurnIndicator,
    PricingRecommendation,
    RecommendedAction,
    RenewalSignal,
    RiskTier,
    Sentiment,
    UsageTrend,
)


class RenewalSignalBuilder:
    """Translate canonical account context into renewal risk and upsell signals."""

    def build(
        self,
        subscription: CanonicalSubscription | None,
        activities: list[CanonicalActivity],
        orders: list[CanonicalOrder],
        cpq_products: list[CanonicalProduct],
        account: CanonicalAccount | None = None,
    ) -> RenewalSignal:
        """Calculate a deterministic `RenewalSignal` for the decision agent."""
        _ = orders, account
        if subscription is None:
            return RenewalSignal(
                risk_score=0.5,
                risk_tier=RiskTier.MEDIUM,
                churn_indicators=[],
                upsell_propensity=0.1,
                expansion_products=[],
                recommended_action=RecommendedAction.STANDARD_RENEWAL,
            )

        escalation_count = subscription.escalation_count_90d
        negative_count = sum(1 for activity in activities if activity.sentiment == Sentiment.NEGATIVE)
        sentiment_component = min(negative_count / len(activities), 1.0) if activities else 0.0
        urgency_component = max(0.0, (90 - subscription.days_to_renewal) / 90)
        risk_score = max(
            0.0,
            min(
                1.0,
                (1.0 - subscription.usage_health_score) * 0.40
                + min(escalation_count / 5.0, 1.0) * 0.25
                + urgency_component * 0.20
                + sentiment_component * 0.15,
            ),
        )
        risk_tier = self._risk_tier(risk_score)
        indicators = self._indicators(subscription, escalation_count, sentiment_component, risk_score)
        expansion_products = self._eligible_products(subscription, cpq_products)
        upsell_propensity = self._upsell_propensity(subscription, expansion_products, risk_tier)
        action = self._recommended_action(risk_tier, upsell_propensity)
        pricing = self._pricing(subscription, risk_tier)
        return RenewalSignal(
            risk_score=risk_score,
            risk_tier=risk_tier,
            churn_indicators=indicators,
            upsell_propensity=upsell_propensity,
            expansion_products=expansion_products,
            recommended_action=action,
            pricing_recommendation=pricing,
        )

    def _risk_tier(self, risk_score: float) -> RiskTier:
        """Bucket the normalized risk score into business-readable tiers."""
        if risk_score >= 0.75:
            return RiskTier.CRITICAL
        if risk_score >= 0.50:
            return RiskTier.HIGH
        if risk_score >= 0.25:
            return RiskTier.MEDIUM
        return RiskTier.LOW

    def _indicators(
        self,
        subscription: CanonicalSubscription,
        escalation_count: int,
        sentiment_component: float,
        risk_score: float,
    ) -> list[ChurnIndicator]:
        """Explain which underlying signals contributed to churn risk."""
        indicators: list[ChurnIndicator] = []
        if subscription.usage_trend == UsageTrend.CRITICAL:
            indicators.append(ChurnIndicator(indicator_type="usage_critical", severity="high", description=f"Usage at {subscription.usage_health_score:.0%} of baseline - critical level"))
        if subscription.usage_trend == UsageTrend.DECLINING:
            indicators.append(ChurnIndicator(indicator_type="usage_declining", severity="medium", description="Usage declining over last 90 days"))
        if escalation_count >= 3:
            indicators.append(ChurnIndicator(indicator_type="multiple_escalations", severity="high", description=f"{escalation_count} escalations in last 90 days"))
        elif escalation_count >= 1:
            indicators.append(ChurnIndicator(indicator_type="has_escalations", severity="medium", description=f"{escalation_count} escalation(s) in last 90 days"))
        if subscription.days_to_renewal <= 30 and risk_score >= 0.50:
            indicators.append(ChurnIndicator(indicator_type="late_stage_risk", severity="high", description=f"High-risk account with only {subscription.days_to_renewal} days to renewal"))
        if sentiment_component > 0.40:
            indicators.append(ChurnIndicator(indicator_type="negative_sentiment_trend", severity="medium", description=f"{sentiment_component:.0%} of recent interactions show negative sentiment"))
        return indicators

    def _eligible_products(
        self,
        subscription: CanonicalSubscription,
        cpq_products: list[CanonicalProduct],
    ) -> list[str]:
        """Find active add-on products compatible with the contracted footprint."""
        return [
            product.product_id
            for product in cpq_products
            if product.is_active
            and product.product_id not in subscription.contracted_products
            and any(base in subscription.contracted_products for base in product.bundle_eligibility)
        ]

    def _upsell_propensity(
        self,
        subscription: CanonicalSubscription,
        expansion_products: list[str],
        risk_tier: RiskTier,
    ) -> float:
        """Score expansion fit while dampening upsell for critical-risk accounts."""
        if subscription.last_expansion_date is None:
            expansion_boost = 0.2
        else:
            months_since = (date.today() - subscription.last_expansion_date).days / 30
            expansion_boost = 0.0 if months_since < 6 else (0.1 if months_since < 18 else 0.2)
        propensity = min(
            subscription.usage_health_score + expansion_boost + min(len(expansion_products) * 0.05, 0.2),
            1.0,
        )
        if risk_tier == RiskTier.CRITICAL:
            return max(0.1, propensity * 0.25)
        return propensity

    def _recommended_action(self, risk_tier: RiskTier, upsell_propensity: float) -> RecommendedAction:
        """Map risk and expansion fit into the sales motion."""
        if risk_tier == RiskTier.CRITICAL:
            return RecommendedAction.ESCALATE_TO_CSM
        if risk_tier == RiskTier.HIGH and upsell_propensity < 0.40:
            return RecommendedAction.SAVE_PLAY
        if risk_tier in {RiskTier.HIGH, RiskTier.MEDIUM}:
            return RecommendedAction.RISK_ADJUSTED_RENEWAL
        return RecommendedAction.STANDARD_RENEWAL

    def _pricing(self, subscription: CanonicalSubscription, risk_tier: RiskTier) -> PricingRecommendation:
        """Calculate the risk-adjusted renewal price recommendation."""
        multipliers = {
            RiskTier.CRITICAL: Decimal("0.88"),
            RiskTier.HIGH: Decimal("0.93"),
            RiskTier.MEDIUM: Decimal("0.97"),
            RiskTier.LOW: Decimal("1.00"),
        }
        adjusted = subscription.arr * multipliers[risk_tier]
        discount = float((subscription.arr - adjusted) / subscription.arr) if subscription.arr else 0.0
        return PricingRecommendation(
            base_price=subscription.arr,
            risk_adjusted_price=adjusted,
            max_discount_pct=discount,
            rationale=f"{risk_tier.value} risk - {discount:.0%} risk adjustment applied",
        )
