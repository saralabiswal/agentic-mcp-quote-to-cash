from context.models import SubProvider
from mcp.adapters.common import SeedSubServer


class OracleSubMCP(SeedSubServer):
    provider = SubProvider.ORACLE_SUBSCRIPTION
