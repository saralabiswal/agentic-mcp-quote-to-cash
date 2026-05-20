# Author: Sarala Biswal
"""MCP adapter module for the Salesforce Oms source-system provider."""
from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class SalesforceOMSMCP(SeedOMSServer):
    provider = OMSProvider.SALESFORCE_OMS
