# Author: Sarala Biswal
"""Tests for models behavior."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from context.models import (
    ActivityType,
    BillingFrequency,
    CanonicalAccount,
    CanonicalActivity,
    CanonicalSubscription,
    Completeness,
    CRMProvider,
    Segment,
    Sentiment,
    SubscriptionStatus,
    UnifiedContext,
    UsageTrend,
)


def test_models_instantiate_and_serialize() -> None:
    account = CanonicalAccount(
        canonical_account_id="ACC-X",
        crm_source=CRMProvider.SALESFORCE,
        crm_source_id="SF-X",
        name="Acme",
        industry="Software",
        segment=Segment.ENTERPRISE,
        account_value=Decimal("100"),
        employee_count=10,
        region="US",
        health_score=0.8,
    )
    subscription = CanonicalSubscription(
        subscription_id="SUB-X",
        account_id="ACC-X",
        status=SubscriptionStatus.ACTIVE,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=20),
        arr=Decimal("100"),
        contracted_products=["P1"],
        billing_frequency=BillingFrequency.ANNUAL,
        usage_health_score=0.5,
        usage_trend=UsageTrend.DECLINING,
        escalation_count_90d=1,
    )
    activity = CanonicalActivity(
        activity_id="A1",
        account_id="ACC-X",
        activity_type=ActivityType.EMAIL,
        activity_date=datetime.now(timezone.utc),
        subject="Hello",
        description="World",
        sentiment=Sentiment.NEUTRAL,
    )
    context = UnifiedContext(
        context_run_id="CTX-X",
        assembled_at=datetime.now(timezone.utc),
        crm_provider=CRMProvider.SALESFORCE,
        oms_provider="oracle_fom",
        sub_provider="oracle_subscription",
        account=account,
        subscription=subscription,
        activities=[activity],
        context_completeness=Completeness.COMPLETE,
    )
    restored = UnifiedContext.model_validate_json(context.model_dump_json())
    assert restored.subscription is not None
    assert restored.subscription.days_to_renewal <= 20


def test_enum_validation_raises() -> None:
    with pytest.raises(ValidationError):
        CanonicalAccount(
            canonical_account_id="ACC-X",
            crm_source="bad",
            crm_source_id="SF-X",
            name="Acme",
            industry="Software",
            segment=Segment.ENTERPRISE,
            account_value=Decimal("100"),
            employee_count=10,
            region="US",
            health_score=0.8,
        )
