# Author: Sarala Biswal
"""MCP adapter module for the Oracle Crm source-system provider."""
from context.models import CRMProvider
from mcp.adapters.common import SeedCRMServer


class OracleCRMMCP(SeedCRMServer):
    provider = CRMProvider.ORACLE_CRM
