# Author: Sarala Biswal
"""MCP adapter module for the Dynamics source-system provider."""
from context.models import CRMProvider
from mcp.adapters.common import SeedCRMServer


class DynamicsMCP(SeedCRMServer):
    provider = CRMProvider.DYNAMICS
