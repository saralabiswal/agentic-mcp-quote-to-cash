from __future__ import annotations

from abc import abstractmethod

from mcp.base import BaseMCPServer


class AbstractSubServer(BaseMCPServer):
    @abstractmethod
    async def get_subscription(self, account_id: str) -> dict[str, object]: ...

    @abstractmethod
    async def get_renewal_signals(self, subscription_id: str) -> dict[str, object]: ...
