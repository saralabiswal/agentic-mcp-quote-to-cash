# Author: Sarala Biswal
"""MCP adapter module for the Oracle Fom source-system provider."""
from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class OracleFOMMCP(SeedOMSServer):
    provider = OMSProvider.ORACLE_FOM
