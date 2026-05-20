# Author: Sarala Biswal
from __future__ import annotations

import pytest

from api.dependencies import Settings
from context.models import InstallBaseProvider
from mcp.adapters.common import map_installed_product
from mcp.factory import MCPFactory


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", list(InstallBaseProvider))
async def test_install_base_adapter_returns_installed_products(provider: InstallBaseProvider) -> None:
    adapter = MCPFactory(Settings(install_base_provider=provider)).get_install_base_server()
    for account_id in ("ACC-001", "ACC-002", "ACC-003"):
        raw_products = await adapter.get_installed_products(account_id)
        products = [map_installed_product(raw) for raw in raw_products]
        assert products
        assert all(product.product_id for product in products)
