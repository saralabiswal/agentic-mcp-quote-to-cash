from context.models import SubProvider
from mcp.adapters.common import SeedSubServer


class ZuoraSubMCP(SeedSubServer):
    provider = SubProvider.ZUORA_SUB
