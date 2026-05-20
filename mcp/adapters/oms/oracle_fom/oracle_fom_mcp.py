from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class OracleFOMMCP(SeedOMSServer):
    provider = OMSProvider.ORACLE_FOM
