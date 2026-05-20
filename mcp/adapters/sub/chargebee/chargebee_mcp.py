# Author: Sarala Biswal
"""MCP adapter module for the Chargebee source-system provider."""
from context.models import SubProvider
from mcp.adapters.common import SeedSubServer


class ChargebeeMCP(SeedSubServer):
    provider = SubProvider.CHARGEBEE
