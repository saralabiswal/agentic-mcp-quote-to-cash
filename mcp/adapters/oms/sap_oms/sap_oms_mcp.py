from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class SAPOMSMCP(SeedOMSServer):
    provider = OMSProvider.SAP_S4HANA
