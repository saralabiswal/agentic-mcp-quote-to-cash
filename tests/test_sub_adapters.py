from __future__ import annotations

import pytest

from api.dependencies import Settings
from context.models import SubProvider
from mcp.adapters.common import map_subscription
from mcp.factory import MCPFactory


@pytest.mark.asyncio
async def test_all_sub_adapters_return_valid_subscriptions_for_all_accounts() -> None:
    for provider in SubProvider:
        adapter = MCPFactory(Settings(sub_provider=provider)).get_sub_server()
        for account_id in ("ACC-001", "ACC-002", "ACC-003"):
            raw = await adapter.get_subscription(account_id)
            subscription = map_subscription(raw, account_id)
            assert subscription.renewal_date is not None
            assert 0.0 <= subscription.usage_health_score <= 1.0
