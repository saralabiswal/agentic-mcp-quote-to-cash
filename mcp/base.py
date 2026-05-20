# Author: Sarala Biswal
"""Base MCP server abstraction that routes calls to demo or real adapter paths."""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from api.dependencies import Settings
from context.models import AppMode


class MCPTimeoutError(TimeoutError):
    """Raised when a source-system adapter exceeds the configured timeout."""

    pass


class MCPConnectionError(ConnectionError):
    """Raised when an adapter call fails outside expected timeout behavior."""

    pass


class BaseMCPServer(ABC):
    """Base class for MCP source-system adapters.

    Concrete adapters implement `_mock_call` and `_real_call`. The base class
    handles mode selection, timeout enforcement, and wrapping unexpected source
    errors in integration-specific exceptions.
    """

    def __init__(self, settings: Settings) -> None:
        """Bind adapter execution to the current runtime settings."""
        self.settings = settings
        self.mode = settings.app_mode
        self.timeout = settings.mcp_timeout_seconds

    async def _call_tool(self, tool_name: str, params: dict[str, Any]) -> Any:
        """Route an adapter tool call to the demo or real implementation path."""
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
        """Return deterministic fixture-backed data for demo mode."""
        raise NotImplementedError

    @abstractmethod
    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> Any:
        """Call or document the real vendor integration path for production mode."""
        raise NotImplementedError
