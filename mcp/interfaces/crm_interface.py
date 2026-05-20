# Author: Sarala Biswal
"""Abstract MCP interface contract for CRM adapters."""
from __future__ import annotations

from abc import abstractmethod

from mcp.base import BaseMCPServer


class AbstractCRMServer(BaseMCPServer):
    @abstractmethod
    async def get_account(self, crm_account_id: str) -> dict[str, object]: ...

    @abstractmethod
    async def get_opportunities(self, crm_account_id: str) -> list[dict[str, object]]: ...

    @abstractmethod
    async def get_contacts(self, crm_account_id: str) -> list[dict[str, object]]: ...

    @abstractmethod
    async def get_activities(self, crm_account_id: str, days: int = 90) -> list[dict[str, object]]: ...
