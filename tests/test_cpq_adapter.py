# Author: Sarala Biswal
"""Tests for cpq adapter behavior."""
from __future__ import annotations

import pytest

from api.dependencies import Settings
from context.models import CanonicalProduct
from mcp.adapters.cpq.oracle_cpq.oracle_cpq_mapper import map_product
from mcp.factory import MCPFactory


@pytest.mark.asyncio
async def test_oracle_cpq_catalog_pricing_and_mapper() -> None:
    adapter = MCPFactory(Settings()).get_cpq_server()
    catalog = await adapter.get_product_catalog("enterprise")
    pricing = await adapter.get_pricing_context("ACC-001", ["P-ENT-CORE"])
    products = [map_product(raw) for raw in catalog]
    assert len(products) == 8
    assert all(isinstance(product, CanonicalProduct) for product in products)
    assert pricing["min_margin_floor"] == 0.18
    assert pricing["approval_discount_threshold"] == 0.25
    assert len(pricing["pricing_tiers"]) >= 3
