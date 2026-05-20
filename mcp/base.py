# Author: Sarala Biswal
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from api.dependencies import Settings
from context.models import AppMode


class MCPTimeoutError(TimeoutError):
    pass


class MCPConnectionError(ConnectionError):
    pass


class BaseMCPServer(ABC):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.mode = settings.app_mode
        self.timeout = settings.mcp_timeout_seconds

    async def _call_tool(self, tool_name: str, params: dict[str, Any]) -> Any:
        try:
            if self.mode == AppMode.DEMO:
                return await asyncio.wait_for(self._mock_call(tool_name, params), self.timeout)
            return await asyncio.wait_for(self._real_call(tool_name, params), self.timeout)
        except TimeoutError as exc:
            raise MCPTimeoutError(f"{self.__class__.__name__}.{tool_name} timed out") from exc
        except NotImplementedError:
            raise
        except Exception as exc:
            raise MCPConnectionError(f"{self.__class__.__name__}.{tool_name} failed: {exc}") from exc

    @abstractmethod
    async def _mock_call(self, tool_name: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError
