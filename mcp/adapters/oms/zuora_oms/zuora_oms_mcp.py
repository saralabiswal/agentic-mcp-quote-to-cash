# Author: Sarala Biswal
from context.models import OMSProvider
from mcp.adapters.common import SeedOMSServer


class ZuoraOMSMCP(SeedOMSServer):
    provider = OMSProvider.ZUORA_OMS
