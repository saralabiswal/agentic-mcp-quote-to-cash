# Author: Sarala Biswal
"""Abstract MCP interface contract for OMS adapters."""
from __future__ import annotations

from abc import abstractmethod

from mcp.base import BaseMCPServer


class AbstractOMSServer(BaseMCPServer):
    @abstractmethod
    async def get_orders(self, account_id: str, months: int = 24) -> list[dict[str, object]]: ...
