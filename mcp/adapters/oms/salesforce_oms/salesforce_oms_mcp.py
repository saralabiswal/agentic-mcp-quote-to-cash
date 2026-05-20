# Author: Sarala Biswal
from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class SalesforceOMSMCP(SeedOMSServer):
    provider = OMSProvider.SALESFORCE_OMS
