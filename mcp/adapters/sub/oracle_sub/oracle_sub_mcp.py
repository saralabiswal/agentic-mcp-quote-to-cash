# Author: Sarala Biswal
"""MCP adapter module for the Oracle Sub source-system provider."""
from context.models import SubProvider
from mcp.adapters.common import SeedSubServer


class OracleSubMCP(SeedSubServer):
    provider = SubProvider.ORACLE_SUBSCRIPTION
