# Author: Sarala Biswal
from __future__ import annotations

from abc import abstractmethod

from mcp.base import BaseMCPServer


class AbstractCPQServer(BaseMCPServer):
    @abstractmethod
    async def get_product_catalog(self, segment: str) -> list[dict[str, object]]: ...

    @abstractmethod
    async def get_pricing_context(self, account_id: str, products: list[str]) -> dict[str, object]: ...

    @abstractmethod
    async def create_quote_draft(self, context: dict[str, object]) -> dict[str, object]: ...
