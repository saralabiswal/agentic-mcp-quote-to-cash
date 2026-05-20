# Author: Sarala Biswal
from __future__ import annotations

import pytest

from api.dependencies import Settings
from context.models import CRMProvider, OMSProvider, SubProvider
from mcp.adapters.common import map_account, map_order, map_subscription
from mcp.factory import MCPFactory


@pytest.mark.asyncio
async def test_all_provider_adapters_return_seed_data() -> None:
    for crm_provider in CRMProvider:
        factory = MCPFactory(Settings(crm_provider=crm_provider))
        raw = await factory.get_crm_server().get_account("ACC-001")
        assert map_account(raw, crm_provider).canonical_account_id == "ACC-001"
    for oms_provider in OMSProvider:
        factory = MCPFactory(Settings(oms_provider=oms_provider))
        orders = await factory.get_oms_server().get_orders("ACC-001")
        assert map_order(orders[0], "ACC-001").account_id == "ACC-001"
    for sub_provider in SubProvider:
        factory = MCPFactory(Settings(sub_provider=sub_provider))
        sub = await factory.get_sub_server().get_subscription("ACC-001")
        assert map_subscription(sub, "ACC-001").renewal_date is not None


@pytest.mark.asyncio
async def test_cpq_catalog_and_install_base() -> None:
    factory = MCPFactory(Settings())
    assert len(await factory.get_cpq_server().get_product_catalog("enterprise")) == 8
    assert await factory.get_install_base_server().get_installed_products("ACC-001")
