# Author: Sarala Biswal
"""Factory that selects concrete MCP adapters from runtime provider settings."""
from __future__ import annotations

from functools import lru_cache

from api.dependencies import Settings
from context.models import CRMProvider, InstallBaseProvider, OMSProvider, SubProvider
from mcp.adapters.cpq.oracle_cpq.oracle_cpq_mcp import OracleCPQMCP
from mcp.adapters.crm.dynamics.dynamics_mcp import DynamicsMCP
from mcp.adapters.crm.oracle_crm.oracle_crm_mcp import OracleCRMMCP
from mcp.adapters.crm.salesforce.salesforce_mcp import SalesforceMCP
from mcp.adapters.install_base.oracle_install_base_mcp import OracleInstallBaseMCP
from mcp.adapters.install_base.salesforce_asset_mcp import SalesforceAssetMCP
from mcp.adapters.install_base.servicenow_cmdb_mcp import ServiceNowCMDBMCP
from mcp.adapters.oms.netsuite_oms.netsuite_oms_mcp import NetsuiteOMSMCP
from mcp.adapters.oms.oracle_fom.oracle_fom_mcp import OracleFOMMCP
from mcp.adapters.oms.salesforce_oms.salesforce_oms_mcp import SalesforceOMSMCP
from mcp.adapters.oms.sap_oms.sap_oms_mcp import SAPOMSMCP
from mcp.adapters.oms.zuora_oms.zuora_oms_mcp import ZuoraOMSMCP
from mcp.adapters.sub.chargebee.chargebee_mcp import ChargebeeMCP
from mcp.adapters.sub.oracle_sub.oracle_sub_mcp import OracleSubMCP
from mcp.adapters.sub.salesforce_revenue.salesforce_rev_mcp import SalesforceRevenueMCP
from mcp.adapters.sub.zuora_sub.zuora_sub_mcp import ZuoraSubMCP
from mcp.interfaces.cpq_interface import AbstractCPQServer
from mcp.interfaces.crm_interface import AbstractCRMServer
from mcp.interfaces.oms_interface import AbstractOMSServer
from mcp.interfaces.sub_interface import AbstractSubServer


class ConfigurationError(ValueError):
    """Raised when runtime stack configuration cannot be mapped to an adapter."""

    pass


InstallBaseAdapter = OracleInstallBaseMCP | SalesforceAssetMCP | ServiceNowCMDBMCP


class MCPFactory:
    """Create the concrete adapter for each configured commercial-system slot."""

    def __init__(self, settings: Settings) -> None:
        """Store the runtime provider settings used for adapter selection."""
        self.settings = settings

    def get_crm_server(self) -> AbstractCRMServer:
        """Return the selected CRM MCP adapter."""
        adapters: dict[CRMProvider, type[AbstractCRMServer]] = {
            CRMProvider.SALESFORCE: SalesforceMCP,
            CRMProvider.DYNAMICS: DynamicsMCP,
            CRMProvider.ORACLE_CRM: OracleCRMMCP,
        }
        return adapters[self.settings.crm_provider](self.settings)

    def get_cpq_server(self) -> AbstractCPQServer:
        """Return the Oracle CPQ adapter, which is always present in this app."""
        return OracleCPQMCP(self.settings)

    def get_oms_server(self) -> AbstractOMSServer:
        """Return the selected Order Management Systems MCP adapter."""
        adapters: dict[OMSProvider, type[AbstractOMSServer]] = {
            OMSProvider.ORACLE_FOM: OracleFOMMCP,
            OMSProvider.SALESFORCE_OMS: SalesforceOMSMCP,
            OMSProvider.SAP_S4HANA: SAPOMSMCP,
            OMSProvider.ZUORA_OMS: ZuoraOMSMCP,
            OMSProvider.NETSUITE: NetsuiteOMSMCP,
        }
        return adapters[self.settings.oms_provider](self.settings)

    def get_sub_server(self) -> AbstractSubServer:
        """Return the selected Subscription Management MCP adapter."""
        adapters: dict[SubProvider, type[AbstractSubServer]] = {
            SubProvider.ORACLE_SUBSCRIPTION: OracleSubMCP,
            SubProvider.ZUORA_SUB: ZuoraSubMCP,
            SubProvider.CHARGEBEE: ChargebeeMCP,
            SubProvider.SALESFORCE_REVENUE: SalesforceRevenueMCP,
        }
        return adapters[self.settings.sub_provider](self.settings)

    def get_install_base_server(self) -> InstallBaseAdapter:
        """Return the selected Install Base or asset-footprint MCP adapter."""
        adapters: dict[InstallBaseProvider, type[InstallBaseAdapter]] = {
            InstallBaseProvider.ORACLE_INSTALL_BASE: OracleInstallBaseMCP,
            InstallBaseProvider.SALESFORCE_ASSET: SalesforceAssetMCP,
            InstallBaseProvider.SERVICENOW_CMDB: ServiceNowCMDBMCP,
        }
        return adapters[self.settings.install_base_provider](self.settings)


@lru_cache(maxsize=1)
def get_factory(settings: Settings) -> MCPFactory:
    """Return a cached factory for dependency-injected call sites."""
    return MCPFactory(settings)
