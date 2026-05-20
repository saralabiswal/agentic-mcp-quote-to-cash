from __future__ import annotations

import pytest

from api.dependencies import Settings
from context.models import CRMProvider
from mcp.adapters.common import map_account, map_activity, map_contact, map_opportunity
from mcp.base import MCPTimeoutError
from mcp.factory import MCPFactory


def comparable_account(provider: CRMProvider, raw: dict[str, object]) -> dict[str, object]:
    account = map_account(raw, provider)
    return account.model_copy(
        update={"crm_source": CRMProvider.SALESFORCE, "crm_source_id": "normalized"}
    ).model_dump(mode="json")


@pytest.mark.asyncio
async def test_all_crm_adapters_return_valid_mock_data_for_all_accounts() -> None:
    for provider in CRMProvider:
        adapter = MCPFactory(Settings(crm_provider=provider)).get_crm_server()
        for account_id in ("ACC-001", "ACC-002", "ACC-003"):
            account = await adapter.get_account(account_id)
            opportunities = await adapter.get_opportunities(account_id)
            contacts = await adapter.get_contacts(account_id)
            activities = await adapter.get_activities(account_id)
            assert map_account(account, provider).canonical_account_id == account_id
            assert map_opportunity(opportunities[0], account_id).account_id == account_id
            assert map_contact(contacts[0], account_id).account_id == account_id
            assert map_activity(activities[0], account_id).account_id == account_id


@pytest.mark.asyncio
async def test_crm_mappers_produce_identical_canonical_output() -> None:
    baseline: dict[str, object] | None = None
    for provider in CRMProvider:
        adapter = MCPFactory(Settings(crm_provider=provider)).get_crm_server()
        current = comparable_account(provider, await adapter.get_account("ACC-002"))
        if baseline is None:
            baseline = current
        assert current == baseline


@pytest.mark.asyncio
async def test_crm_timeout_raises_for_all_adapters() -> None:
    for provider in CRMProvider:
        adapter = MCPFactory(Settings(crm_provider=provider, mcp_timeout_seconds=0)).get_crm_server()
        with pytest.raises(MCPTimeoutError):
            await adapter.get_account("ACC-001")
