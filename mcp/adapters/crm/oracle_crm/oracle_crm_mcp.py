from context.models import CRMProvider
from mcp.adapters.common import SeedCRMServer


class OracleCRMMCP(SeedCRMServer):
    provider = CRMProvider.ORACLE_CRM
