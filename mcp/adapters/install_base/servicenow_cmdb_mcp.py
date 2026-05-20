from __future__ import annotations

from typing import Any, cast

from mcp.base import BaseMCPServer
from seed_data.loader import load_json, require_account


class ServiceNowCMDBMCP(BaseMCPServer):
    async def get_installed_products(self, account_id: str) -> list[dict[str, object]]:
        return cast(list[dict[str, object]], await self._call_tool("get_installed_products", {"account_id": account_id}))

    async def _mock_call(self, tool_name: str, params: dict[str, Any]) -> object:
        if tool_name != "get_installed_products":
            raise KeyError(tool_name)
        return require_account(load_json("install_base.json"), str(params["account_id"]))

    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> object:
        raise NotImplementedError(
            "ServiceNow CMDB real stub: query cmdb_ci and contract entitlement tables through "
            "/api/now/table using OAuth2 or basic auth, then map configuration items into the "
            "canonical InstalledProduct and Entitlement objects."
        )
