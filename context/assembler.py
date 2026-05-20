# Author: Sarala Biswal
"""Context orchestration module that concurrently assembles canonical customer truth from selected adapters."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

from agents.renewal_signal_builder import RenewalSignalBuilder
from api.dependencies import Settings
from context.conflict_resolver import ConflictResolver
from context.models import (
    CanonicalAccount,
    Completeness,
    CRMProvider,
    Segment,
    SourceAttribution,
    UnifiedContext,
)
from context.normalizer import Normalizer
from context.validator import ContextValidator
from mcp.factory import MCPFactory


class ContextAssembler:
    """Build the canonical commercial context used by the decision agent.

    The assembler is intentionally tolerant of source failures. It fans out to
    the selected MCP adapters concurrently, records failed sources as missing
    evidence, and still returns a `UnifiedContext` so the decision layer can
    apply governance flags instead of crashing the user flow.
    """

    def __init__(self, settings: Settings, factory: MCPFactory | None = None) -> None:
        """Create an assembler for the current runtime stack selection."""
        self.settings = settings
        self.factory = factory or MCPFactory(settings)
        self.normalizer = Normalizer()
        self.resolver = ConflictResolver()
        self.validator = ContextValidator()

    async def assemble(self, account_id: str, force_refresh: bool = False) -> UnifiedContext:
        """Assemble context for an account while enforcing the configured timeout.

        `force_refresh` is accepted as part of the public API contract for a
        future cache-aware implementation. The current implementation always
        assembles fresh demo/live context.
        """
        _ = force_refresh
        try:
            return await asyncio.wait_for(
                self._assemble_inner(account_id),
                timeout=self.settings.context_assembly_timeout_seconds,
            )
        except Exception as exc:
            return self._fallback_context(account_id, [f"assembly:{exc.__class__.__name__}"])

    async def _assemble_inner(self, account_id: str) -> UnifiedContext:
        """Run all adapter calls concurrently and normalize successful results."""
        crm = self.factory.get_crm_server()
        cpq = self.factory.get_cpq_server()
        oms = self.factory.get_oms_server()
        sub = self.factory.get_sub_server()
        install_base = self.factory.get_install_base_server()

        results = await asyncio.gather(
            crm.get_account(account_id),
            crm.get_opportunities(account_id),
            crm.get_contacts(account_id),
            crm.get_activities(account_id, days=90),
            cpq.get_product_catalog("all"),
            cpq.get_pricing_context(account_id, []),
            oms.get_orders(account_id, months=24),
            sub.get_subscription(account_id),
            sub.get_renewal_signals(f"SUB-{account_id[-3:]}"),
            install_base.get_installed_products(account_id),
            return_exceptions=True,
        )

        names = [
            "crm_account",
            "crm_opportunities",
            "crm_contacts",
            "crm_activities",
            "cpq_catalog",
            "cpq_pricing",
            "orders",
            "subscription",
            "subscription_signals",
            "install_base",
        ]
        missing = [name for name, result in zip(names, results, strict=True) if isinstance(result, Exception)]

        parts: dict[str, Any] = {}
        if not any(name.startswith("crm_") for name in missing):
            parts.update(
                self.normalizer.normalize_crm(
                    results[0],  # type: ignore[arg-type]
                    results[1],  # type: ignore[arg-type]
                    results[2],  # type: ignore[arg-type]
                    results[3],  # type: ignore[arg-type]
                    self.settings.crm_provider,
                    account_id,
                )
            )
        if "cpq_catalog" not in missing:
            parts.update(self.normalizer.normalize_cpq(results[4]))  # type: ignore[arg-type]
        if "orders" not in missing:
            parts.update(self.normalizer.normalize_oms(results[6], self.settings.oms_provider, account_id))  # type: ignore[arg-type]
        if "subscription" not in missing:
            parts.update(self.normalizer.normalize_sub(results[7], self.settings.sub_provider, account_id))  # type: ignore[arg-type]
        if self.settings.install_base_enabled and "install_base" not in missing:
            parts.update(self.normalizer.normalize_install_base(results[9]))  # type: ignore[arg-type]

        if "account" not in parts:
            return self._fallback_context(account_id, missing or ["crm"])

        resolved, resolutions = self.resolver.resolve(parts)
        account = resolved["account"]
        subscription = resolved.get("subscription")
        activities = resolved.get("activities", [])
        orders = resolved.get("orders", [])
        products = resolved.get("products", [])
        renewal_signal = RenewalSignalBuilder().build(subscription, activities, orders, products, account)
        missing_sources = self._coalesce_missing(missing)
        completeness = self.validator.validate(missing_sources)

        return UnifiedContext(
            context_run_id=f"CTX-{uuid4()}",
            assembled_at=datetime.now(timezone.utc),
            crm_provider=self.settings.crm_provider,
            oms_provider=self.settings.oms_provider,
            sub_provider=self.settings.sub_provider,
            install_base_provider=self.settings.install_base_provider,
            account=account,
            opportunity=resolved.get("opportunity"),
            contacts=resolved.get("contacts", []),
            subscription=subscription,
            orders=orders,
            activities=activities,
            products=products,
            renewal_signal=renewal_signal,
            source_attribution=self._attribution(resolved),
            conflict_resolutions=resolutions,
            context_completeness=completeness,
            missing_sources=missing_sources,
        )

    def _fallback_context(self, account_id: str, missing: list[str]) -> UnifiedContext:
        """Return a degraded context when the account cannot be safely assembled."""
        account = CanonicalAccount(
            canonical_account_id=account_id,
            crm_source=CRMProvider.SALESFORCE,
            crm_source_id=account_id,
            name="Unknown Account",
            industry="Unknown",
            segment=Segment.ENTERPRISE,
            account_value=Decimal("0"),
            employee_count=None,
            region="unknown",
            health_score=0,
        )
        return UnifiedContext(
            context_run_id=f"CTX-{uuid4()}",
            assembled_at=datetime.now(timezone.utc),
            crm_provider=self.settings.crm_provider,
            oms_provider=self.settings.oms_provider,
            sub_provider=self.settings.sub_provider,
            install_base_provider=self.settings.install_base_provider,
            account=account,
            context_completeness=Completeness.DEGRADED,
            missing_sources=missing,
        )

    def _coalesce_missing(self, missing: list[str]) -> list[str]:
        """Collapse low-level failed calls into business source categories."""
        sources: list[str] = []
        if any(name.startswith("crm_") for name in missing):
            sources.append("crm")
        if any(name.startswith("cpq_") for name in missing):
            sources.append("cpq")
        if "orders" in missing:
            sources.append("oms")
        if "subscription" in missing or "subscription_signals" in missing:
            sources.append("subscription")
        if "install_base" in missing:
            sources.append("install_base")
        return sources

    def _attribution(self, parts: dict[str, Any]) -> dict[str, SourceAttribution]:
        """Attach simple field-level source attribution for normalized parts."""
        return {
            key: SourceAttribution(source=key, field_path=key)
            for key in parts
            if key in {"account", "opportunity", "contacts", "subscription", "orders", "activities", "products"}
        }
