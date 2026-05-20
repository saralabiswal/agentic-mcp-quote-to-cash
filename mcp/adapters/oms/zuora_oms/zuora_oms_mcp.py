# Author: Sarala Biswal
"""MCP adapter module for the Zuora Oms source-system provider."""
from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class ZuoraOMSMCP(SeedOMSServer):
    provider = OMSProvider.ZUORA_OMS
