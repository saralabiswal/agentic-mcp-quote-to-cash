# Author: Sarala Biswal
"""Tests for mcp base behavior."""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from api.dependencies import Settings
from mcp.base import BaseMCPServer, MCPTimeoutError
from mcp.interfaces.crm_interface import AbstractCRMServer


class SlowServer(BaseMCPServer):
    async def _mock_call(self, tool_name: str, params: dict[str, Any]) -> object:
        await asyncio.sleep(0.05)
        return {}

    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> object:
        return {"real": True}


class RouteServer(BaseMCPServer):
    async def _mock_call(self, tool_name: str, params: dict[str, Any]) -> object:
        return {"mode": "mock", "tool": tool_name}

    async def _real_call(self, tool_name: str, params: dict[str, Any]) -> object:
        return {"mode": "real", "tool": tool_name}


@pytest.mark.asyncio
async def test_timeout() -> None:
    server = SlowServer(Settings(mcp_timeout_seconds=0))
    with pytest.raises(MCPTimeoutError):
        await server._call_tool("x", {})


@pytest.mark.asyncio
async def test_real_mode_routes_to_real() -> None:
    server = SlowServer(Settings(app_mode="real"))
    assert await server._call_tool("x", {}) == {"real": True}


@pytest.mark.asyncio
async def test_demo_mode_routes_to_mock() -> None:
    server = RouteServer(Settings(app_mode="demo"))
    assert await server._call_tool("x", {}) == {"mode": "mock", "tool": "x"}


def test_abstract_interface_enforcement() -> None:
    with pytest.raises(TypeError):
        AbstractCRMServer(Settings())  # type: ignore[abstract]
