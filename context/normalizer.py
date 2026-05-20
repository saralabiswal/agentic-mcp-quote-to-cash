# Author: Sarala Biswal
"""Normalization module that converts adapter outputs into canonical context fragments."""
from __future__ import annotations

from typing import Any

from context.models import CRMProvider, OMSProvider, SubProvider
from mcp.adapters.common import (
    map_account,
    map_activity,
    map_contact,
    map_installed_product,
    map_opportunity,
    map_order,
    map_subscription,
)
from mcp.adapters.cpq.oracle_cpq.oracle_cpq_mapper import map_product


class Normalizer:
    """Convert raw adapter responses into the fragments used by `UnifiedContext`."""

    def normalize_crm(
        self,
        account: dict[str, Any],
        opportunities: list[dict[str, Any]],
        contacts: list[dict[str, Any]],
        activities: list[dict[str, Any]],
        provider: CRMProvider,
        account_id: str,
    ) -> dict[str, Any]:
        """Normalize CRM account, opportunity, contact, and activity data."""
        return {
            "account": map_account(account, provider),
            "opportunity": map_opportunity(opportunities[0], account_id) if opportunities else None,
            "contacts": [map_contact(c, account_id) for c in contacts],
            "activities": [map_activity(a, account_id) for a in activities],
        }

    def normalize_cpq(self, products: list[dict[str, Any]]) -> dict[str, Any]:
        """Normalize Oracle CPQ product catalogue data."""
        return {"products": [map_product(p) for p in products]}

    def normalize_oms(self, orders: list[dict[str, Any]], provider: OMSProvider, account_id: str) -> dict[str, Any]:
        """Normalize Order Management Systems order data."""
        _ = provider
        return {"orders": [map_order(o, account_id) for o in orders]}

    def normalize_sub(self, subscription: dict[str, Any], provider: SubProvider, account_id: str) -> dict[str, Any]:
        """Normalize Subscription Management renewal data."""
        _ = provider
        return {"subscription": map_subscription(subscription, account_id)}

    def normalize_install_base(self, products: list[dict[str, Any]]) -> dict[str, Any]:
        """Normalize Install Base or asset-management footprint data."""
        return {"installed_base": [map_installed_product(p) for p in products]}
