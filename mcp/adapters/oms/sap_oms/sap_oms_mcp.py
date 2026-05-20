# Author: Sarala Biswal
"""MCP adapter module for the Sap Oms source-system provider."""
from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class SAPOMSMCP(SeedOMSServer):
    provider = OMSProvider.SAP_S4HANA
