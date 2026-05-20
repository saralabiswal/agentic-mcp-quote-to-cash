# Author: Sarala Biswal
"""MCP adapter module for the Salesforce source-system provider."""
from context.models import CRMProvider
from mcp.adapters.common import SeedCRMServer


class SalesforceMCP(SeedCRMServer):
    provider = CRMProvider.SALESFORCE
