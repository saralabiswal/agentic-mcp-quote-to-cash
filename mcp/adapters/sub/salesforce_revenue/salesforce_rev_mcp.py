# Author: Sarala Biswal
from context.models import SubProvider
from mcp.adapters.common import SeedSubServer


class SalesforceRevenueMCP(SeedSubServer):
    provider = SubProvider.SALESFORCE_REVENUE
