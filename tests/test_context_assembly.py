# Author: Sarala Biswal
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from typing import Any

import pytest

from api.dependencies import Settings
from context.assembler import ContextAssembler
from context.conflict_resolver import ConflictResolver
from context.models import Completeness, CRMProvider, SubProvider
from mcp.adapters.oms.oracle_fom.oracle_fom_mcp import OracleFOMMCP
from mcp.adapters.sub.oracle_sub.oracle_sub_mcp import OracleSubMCP
from mcp.base import MCPTimeoutError
from mcp.factory import MCPFactory


@pytest.mark.asyncio
async def test_context_complete_and_vendor_agnostic() -> None:
    baseline = None
    for crm_provider in CRMProvider:
        for sub_provider in SubProvider:
            context = await ContextAssembler(
                Settings(crm_provider=crm_provider, sub_provider=sub_provider)
            ).assemble("ACC-002")
            assert context.context_completeness == Completeness.COMPLETE
            current = context.account.model_copy(
                update={"crm_source": CRMProvider.SALESFORCE, "crm_source_id": "normalized"}
            )
            if baseline is None:
                baseline = current
            assert current == baseline


@pytest.mark.asyncio
async def test_context_never_raises_for_unknown_account() -> None:
    context = await ContextAssembler(Settings()).assemble("NOPE")
    assert context.context_completeness == Completeness.DEGRADED


class FailingSubMCP(OracleSubMCP):
    async def get_subscription(self, account_id: str) -> dict[str, object]:
        raise MCPTimeoutError("subscription timeout")

    async def get_renewal_signals(self, subscription_id: str) -> dict[str, object]:
        raise MCPTimeoutError("subscription signal timeout")


class FailingOMSMCP(OracleFOMMCP):
    async def get_orders(self, account_id: str, months: int = 24) -> list[dict[str, object]]:
        raise MCPTimeoutError("oms timeout")


class PartialFactory(MCPFactory):
    def __init__(self, settings: Settings, fail_sub: bool = False, fail_oms: bool = False) -> None:
        super().__init__(settings)
        self.fail_sub = fail_sub
        self.fail_oms = fail_oms

    def get_sub_server(self) -> FailingSubMCP | OracleSubMCP:
        if self.fail_sub:
            return FailingSubMCP(self.settings)
        return OracleSubMCP(self.settings)

    def get_oms_server(self) -> FailingOMSMCP | OracleFOMMCP:
        if self.fail_oms:
            return FailingOMSMCP(self.settings)
        return OracleFOMMCP(self.settings)


@pytest.mark.asyncio
async def test_sub_timeout_returns_partial_context() -> None:
    settings = Settings()
    context = await ContextAssembler(settings, PartialFactory(settings, fail_sub=True)).assemble("ACC-001")
    assert context.context_completeness == Completeness.PARTIAL
    assert context.missing_sources == ["subscription"]


@pytest.mark.asyncio
async def test_sub_and_oms_timeout_returns_degraded_context() -> None:
    settings = Settings()
    context = await ContextAssembler(
        settings,
        PartialFactory(settings, fail_sub=True, fail_oms=True),
    ).assemble("ACC-001")
    assert context.context_completeness == Completeness.DEGRADED
    assert set(context.missing_sources) == {"subscription", "oms"}


@pytest.mark.asyncio
async def test_conflict_rules_record_account_value_and_renewal_date() -> None:
    context = await ContextAssembler(Settings()).assemble("ACC-001")
    lower_account = context.account.model_copy(update={"account_value": Decimal("10")})
    higher_account = context.account.model_copy(update={"account_value": Decimal("999999")})
    parts: dict[str, Any] = {
        "account_candidates": [("crm", lower_account), ("subscription", higher_account)],
        "opportunity": context.opportunity,
        "subscription": context.subscription,
    }
    resolved, resolutions = ConflictResolver().resolve(deepcopy(parts))
    assert resolved["account"].account_value == Decimal("999999")
    assert any(item.field_path == "account.account_value" for item in resolutions)
    assert any(item.field_path == "subscription.renewal_date" for item in resolutions)
