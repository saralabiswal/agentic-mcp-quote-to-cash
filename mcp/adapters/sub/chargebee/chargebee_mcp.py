from context.models import SubProvider
from mcp.adapters.common import SeedSubServer


class ChargebeeMCP(SeedSubServer):
    provider = SubProvider.CHARGEBEE
