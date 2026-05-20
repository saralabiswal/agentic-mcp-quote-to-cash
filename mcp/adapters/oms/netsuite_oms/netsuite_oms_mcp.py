# Author: Sarala Biswal
"""MCP adapter module for the Netsuite Oms source-system provider."""
from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class NetsuiteOMSMCP(SeedOMSServer):
    provider = OMSProvider.NETSUITE
