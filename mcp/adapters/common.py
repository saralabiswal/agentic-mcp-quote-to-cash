# Author: Sarala Biswal
from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any, ClassVar, cast

from context.models import (
    ActivityType,
    BillingFrequency,
    CanonicalAccount,
    CanonicalActivity,
    CanonicalContact,
    CanonicalOpportunity,
    CanonicalOrder,
    CanonicalProduct,
    CanonicalSubscription,
    ConfigRule,
    ContactRole,
    CRMProvider,
    InstalledProduct,
    OMSProvider,
    OpportunityStage,
    OpportunityType,
    OrderLineItem,
    OrderStatus,
    OrderType,
    PricingTier,
    Segment,
    Sentiment,
    SubProvider,
    SubscriptionStatus,
    UsageTrend,
)
from mcp.interfaces.cpq_interface import AbstractCPQServer
from mcp.interfaces.crm_interface import AbstractCRMServer
from mcp.interfaces.oms_interface import AbstractOMSServer
from mcp.interfaces.sub_interface import AbstractSubServer
from seed_data.loader import day, load_json, moment, require_account

JsonDict = dict[str, Any]


def _decimal(value: object) -> Decimal:
    return Decimal(str(value))


def _close_date(raw: JsonDict) -> date:
    resolved = day(cast(int, raw["close_offset_days"]))
    if resolved is None:
        raise ValueError("close_offset_days is required")
    return resolved


def map_account(raw: JsonDict, provider: CRMProvider) -> CanonicalAccount:
    c = cast(JsonDict, raw["canonical"])
    source = cast(JsonDict, raw[provider.value])
    source_id = str(
        source.get("Id") or source.get("accountid") or source.get("PartyId") or c["canonical_account_id"]
    )
    return CanonicalAccount(
        canonical_account_id=str(c["canonical_account_id"]),
        crm_source=provider,
        crm_source_id=source_id,
        name=str(c["name"]),
        industry=str(c["industry"]),
        segment=Segment(str(c["segment"])),
        account_value=_decimal(c["account_value"]),
        employee_count=cast(int | None, c.get("employee_count")),
        region=str(c["region"]),
        health_score=float(c["health_score"]),
        last_activity_date=datetime(2026, 1, 1, tzinfo=UTC),
        owner_name=cast(str | None, c.get("owner_name")),
    )


def map_opportunity(raw: JsonDict, account_id: str) -> CanonicalOpportunity:
    return CanonicalOpportunity(
        opportunity_id=str(raw["opportunity_id"]),
        account_id=account_id,
        name=str(raw["name"]),
        opportunity_type=OpportunityType(str(raw["type"])),
        stage=OpportunityStage(str(raw["stage"])),
        amount=_decimal(raw["amount"]),
        close_date=_close_date(raw),
        probability=float(raw["probability"]),
    )


def map_contact(raw: JsonDict, account_id: str) -> CanonicalContact:
    return CanonicalContact(
        contact_id=str(raw["contact_id"]),
        account_id=account_id,
        full_name=str(raw["full_name"]),
        email=str(raw["email"]),
        title=cast(str | None, raw.get("title")),
        role=ContactRole(str(raw["role"])),
        is_primary=bool(raw.get("is_primary", False)),
    )


def map_activity(raw: JsonDict, account_id: str) -> CanonicalActivity:
    return CanonicalActivity(
        activity_id=str(raw["activity_id"]),
        account_id=account_id,
        activity_type=ActivityType(str(raw["activity_type"])),
        activity_date=moment(cast(int, raw["offset_days"])),
        subject=str(raw["subject"]),
        description=str(raw["description"]),
        sentiment=Sentiment(str(raw["sentiment"])),
    )


def map_subscription(raw: JsonDict, account_id: str) -> CanonicalSubscription:
    start = day(cast(int, raw["start_offset_days"]))
    renewal = day(cast(int, raw["renewal_offset_days"]))
    if start is None or renewal is None:
        raise ValueError("subscription dates are required")
    return CanonicalSubscription(
        subscription_id=str(raw["subscription_id"]),
        account_id=account_id,
        status=SubscriptionStatus(str(raw["status"])),
        start_date=start,
        renewal_date=renewal,
        arr=_decimal(raw["arr"]),
        contracted_products=[str(p) for p in cast(list[object], raw["contracted_products"])],
        billing_frequency=BillingFrequency(str(raw["billing_frequency"])),
        usage_health_score=float(raw["usage_health_score"]),
        usage_trend=UsageTrend(str(raw["usage_trend"])),
        escalation_count_90d=int(raw["escalation_count_90d"]),
        last_expansion_date=day(cast(int | None, raw.get("last_expansion_offset_days"))),
    )


def map_order(raw: JsonDict, account_id: str) -> CanonicalOrder:
    ordered = day(cast(int, raw["ordered_offset_days"]))
    if ordered is None:
        raise ValueError("ordered date is required")
    return CanonicalOrder(
        order_id=str(raw["order_id"]),
        account_id=account_id,
        order_number=str(raw["order_number"]),
        order_type=OrderType(str(raw["order_type"])),
        status=OrderStatus(str(raw["status"])),
        ordered_date=ordered,
        total_amount=_decimal(raw["total_amount"]),
        line_items=[
            OrderLineItem(
                product_id=str(item["product_id"]),
                product_name=str(item["product_name"]),
                quantity=int(item["quantity"]),
                unit_price=_decimal(item["unit_price"]),
                line_amount=_decimal(item["line_amount"]),
            )
            for item in cast(list[JsonDict], raw["line_items"])
        ],
    )


def map_installed_product(raw: JsonDict) -> InstalledProduct:
    install = day(cast(int, raw["install_offset_days"]))
    if install is None:
        raise ValueError("install date is required")
    return InstalledProduct(
        product_id=str(raw["product_id"]),
        product_name=str(raw["product_name"]),
        quantity=int(raw["quantity"]),
        install_date=install,
        location=cast(str | None, raw.get("location")),
        support_level=cast(str | None, raw.get("support_level")),
        end_of_support_date=day(cast(int | None, raw.get("end_of_support_offset_days"))),
    )


def product_catalog() -> list[CanonicalProduct]:
    tiers_all = [
        PricingTier(segment=Segment.ENTERPRISE, min_quantity=1, list_price=Decimal("60000"), discount_pct=0),
        PricingTier(segment=Segment.MID_MARKET, min_quantity=1, list_price=Decimal("28000"), discount_pct=0),
        PricingTier(segment=Segment.SMB, min_quantity=1, list_price=Decimal("12000"), discount_pct=0),
    ]
    return [
        CanonicalProduct(product_id="P-ENT-CORE", name="EnterpriseCore", category="platform", is_active=True, bundle_eligibility=[], pricing_tiers=tiers_all, config_rules=[]),
        CanonicalProduct(product_id="P-ANALYTICS", name="AnalyticsPro", category="addon", is_active=True, bundle_eligibility=["P-ENT-CORE"], pricing_tiers=[PricingTier(segment=Segment.ENTERPRISE, min_quantity=1, list_price=Decimal("24000"), discount_pct=0)], config_rules=[]),
        CanonicalProduct(product_id="P-SEC", name="SecurityBundle", category="security", is_active=True, bundle_eligibility=["P-ENT-CORE", "P-MM-SUITE"], pricing_tiers=[PricingTier(segment=Segment.ENTERPRISE, min_quantity=1, list_price=Decimal("18000"), discount_pct=0)], config_rules=[]),
        CanonicalProduct(product_id="P-MM-SUITE", name="MidMarketSuite", category="platform", is_active=True, bundle_eligibility=[], pricing_tiers=[PricingTier(segment=Segment.MID_MARKET, min_quantity=1, list_price=Decimal("28000"), discount_pct=0)], config_rules=[]),
        CanonicalProduct(product_id="P-API", name="APIAccess", category="addon", is_active=True, bundle_eligibility=["P-ENT-CORE", "P-MM-SUITE"], pricing_tiers=[PricingTier(segment=Segment.ENTERPRISE, min_quantity=1, list_price=Decimal("12000"), discount_pct=0)], config_rules=[]),
        CanonicalProduct(product_id="P-SUPPORT", name="SupportPremium", category="support", is_active=True, bundle_eligibility=["P-ENT-CORE", "P-MM-SUITE"], pricing_tiers=[PricingTier(segment=Segment.ENTERPRISE, min_quantity=1, list_price=Decimal("8000"), discount_pct=0)], config_rules=[]),
        CanonicalProduct(product_id="P-ONBOARD", name="OnboardingServices", category="services", is_active=True, bundle_eligibility=["P-ENT-CORE", "P-MM-SUITE"], pricing_tiers=[PricingTier(segment=Segment.ENTERPRISE, min_quantity=1, list_price=Decimal("5000"), discount_pct=0)], config_rules=[ConfigRule(rule_id="one-time", description="One-time service")]),
        CanonicalProduct(product_id="P-TRAIN", name="TrainingBundle", category="services", is_active=True, bundle_eligibility=["P-ENT-CORE", "P-MM-SUITE"], pricing_tiers=[PricingTier(segment=Segment.ENTERPRISE, min_quantity=1, list_price=Decimal("3000"), discount_pct=0)], config_rules=[]),
    ]


class SeedCRMServer(AbstractCRMServer):
    provider: ClassVar[CRMProvider]

    async def get_account(self, crm_account_id: str) -> dict[str, object]:
        return cast(dict[str, object], await self._call_tool("get_account", {"account_id": crm_account_id}))

    async def get_opportunities(self, crm_account_id: str) -> list[dict[str, object]]:
        return cast(list[dict[str, object]], await self._call_tool("get_opportunities", {"account_id": crm_account_id}))

    async def get_contacts(self, crm_account_id: str) -> list[dict[str, object]]:
        return cast(list[dict[str, object]], await self._call_tool("get_contacts", {"account_id": crm_account_id}))

    async def get_activities(self, crm_account_id: str, days: int = 90) -> list[dict[str, object]]:
        return cast(list[dict[str, object]], await self._call_tool("get_activities", {"account_id": crm_account_id, "days": days}))

    async def _mock_call(self, tool_name: str, params: dict[str, Any]) -> object:
        account_id = str(params["account_id"])
        if tool_name == "get_account":
            return require_account(load_json("accounts.json"), account_id)
        if tool_name == "get_opportunities":
            return [require_account(load_json("opportunities.json"), account_id)]
        if tool_name == "get_contacts":
            return require_account(load_json("contacts.json"), account_id)
        if tool_name == "get_activities":
            return require_account(load_json("activities.json"), account_id)
        raise KeyError(tool_name)

    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> object:
        raise NotImplementedError(
            f"{self.__class__.__name__}.{tool_name} documents the vendor REST API path; "
            "wire credentials in real mode before enabling live calls."
        )


class OracleCPQMCPBase(AbstractCPQServer):
    async def get_product_catalog(self, segment: str) -> list[dict[str, object]]:
        return cast(list[dict[str, object]], await self._call_tool("get_product_catalog", {"segment": segment}))

    async def get_pricing_context(self, account_id: str, products: list[str]) -> dict[str, object]:
        return cast(dict[str, object], await self._call_tool("get_pricing_context", {"account_id": account_id, "products": products}))

    async def create_quote_draft(self, context: dict[str, object]) -> dict[str, object]:
        return cast(dict[str, object], await self._call_tool("create_quote_draft", context))

    async def _mock_call(self, tool_name: str, params: dict[str, Any]) -> object:
        if tool_name == "get_product_catalog":
            return [p.model_dump(mode="json") for p in product_catalog()]
        if tool_name == "get_pricing_context":
            account_id = str(params["account_id"])
            sub = map_subscription(require_account(load_json("subscriptions.json"), account_id), account_id)
            return {
                "account_id": account_id,
                "list_price": str(sub.arr),
                "min_margin_floor": 0.18,
                "approval_discount_threshold": 0.25,
                "pricing_tiers": [
                    {"segment": "enterprise", "volume_break": 100, "discount_pct": 0.05},
                    {"segment": "enterprise", "volume_break": 500, "discount_pct": 0.12},
                    {"segment": "mid_market", "volume_break": 100, "discount_pct": 0.04},
                    {"segment": "smb", "volume_break": 100, "discount_pct": 0.02},
                ],
            }
        if tool_name == "create_quote_draft":
            return {"quote_id": "Q-DRAFT", "status": "draft", "input": params}
        raise KeyError(tool_name)

    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> object:
        raise NotImplementedError(
            "Oracle CPQ real path: GET /rest/v1/catalogs/{catalog_id}/products, "
            "POST /rest/v1/priceList/calculate, POST /rest/v1/quotes with X-API-KEY."
        )


class SeedOMSServer(AbstractOMSServer):
    provider: ClassVar[OMSProvider]

    async def get_orders(self, account_id: str, months: int = 24) -> list[dict[str, object]]:
        return cast(list[dict[str, object]], await self._call_tool("get_orders", {"account_id": account_id, "months": months}))

    async def _mock_call(self, tool_name: str, params: dict[str, Any]) -> object:
        if tool_name != "get_orders":
            raise KeyError(tool_name)
        return require_account(load_json("orders.json"), str(params["account_id"]))

    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> object:
        raise NotImplementedError(
            f"{self.__class__.__name__} real API stub documents {self.provider.value} order retrieval "
            "and auth. Replace this with a configured REST client in real mode."
        )


class SeedSubServer(AbstractSubServer):
    provider: ClassVar[SubProvider]

    async def get_subscription(self, account_id: str) -> dict[str, object]:
        return cast(dict[str, object], await self._call_tool("get_subscription", {"account_id": account_id}))

    async def get_renewal_signals(self, subscription_id: str) -> dict[str, object]:
        return cast(dict[str, object], await self._call_tool("get_renewal_signals", {"subscription_id": subscription_id}))

    async def _mock_call(self, tool_name: str, params: dict[str, Any]) -> object:
        if tool_name == "get_subscription":
            return require_account(load_json("subscriptions.json"), str(params["account_id"]))
        if tool_name == "get_renewal_signals":
            subs = cast(dict[str, JsonDict], load_json("subscriptions.json"))
            for sub in subs.values():
                if sub["subscription_id"] == params["subscription_id"]:
                    return {"subscription_id": params["subscription_id"], "usage_health_score": sub["usage_health_score"], "escalation_count_90d": sub["escalation_count_90d"]}
            raise KeyError(params["subscription_id"])
        raise KeyError(tool_name)

    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> object:
        raise NotImplementedError(
            f"{self.__class__.__name__} real API stub documents {self.provider.value} subscription "
            "retrieval and auth. Replace this with a configured REST client in real mode."
        )
