# Author: Sarala Biswal
from context.models import CRMProvider
from mcp.adapters.common import SeedCRMServer


class DynamicsMCP(SeedCRMServer):
    provider = CRMProvider.DYNAMICS
