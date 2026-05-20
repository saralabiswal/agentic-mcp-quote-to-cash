# Author: Sarala Biswal
"""MCP adapter module for the Salesforce Rev source-system provider."""
from context.models import SubProvider
from mcp.adapters.common import SeedSubServer


class SalesforceRevenueMCP(SeedSubServer):
    provider = SubProvider.SALESFORCE_REVENUE
