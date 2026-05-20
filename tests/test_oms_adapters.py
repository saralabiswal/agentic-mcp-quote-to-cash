# Author: Sarala Biswal
from __future__ import annotations

import pytest

from api.dependencies import Settings
from context.models import OMSProvider
from mcp.adapters.common import map_order
from mcp.factory import MCPFactory


def comparable_order(raw: dict[str, object], account_id: str) -> dict[str, object]:
    return map_order(raw, account_id).model_dump(mode="json")


@pytest.mark.asyncio
async def test_all_oms_adapters_return_valid_orders_for_all_accounts() -> None:
    for provider in OMSProvider:
        adapter = MCPFactory(Settings(oms_provider=provider)).get_oms_server()
        for account_id in ("ACC-001", "ACC-002", "ACC-003"):
            orders = await adapter.get_orders(account_id)
            assert orders
            assert map_order(orders[0], account_id).account_id == account_id


@pytest.mark.asyncio
async def test_oms_mappers_produce_identical_order_output() -> None:
    baseline: list[dict[str, object]] | None = None
    for provider in OMSProvider:
        orders = await MCPFactory(Settings(oms_provider=provider)).get_oms_server().get_orders("ACC-001")
        current = [comparable_order(order, "ACC-001") for order in orders]
        if baseline is None:
            baseline = current
        assert current == baseline
