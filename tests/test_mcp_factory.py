# Author: Sarala Biswal
from __future__ import annotations

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
from mcp.factory import MCPFactory


def test_factory_returns_correct_adapter_types() -> None:
    crm_types = {
        CRMProvider.SALESFORCE: SalesforceMCP,
        CRMProvider.DYNAMICS: DynamicsMCP,
        CRMProvider.ORACLE_CRM: OracleCRMMCP,
    }
    oms_types = {
        OMSProvider.ORACLE_FOM: OracleFOMMCP,
        OMSProvider.SALESFORCE_OMS: SalesforceOMSMCP,
        OMSProvider.SAP_S4HANA: SAPOMSMCP,
        OMSProvider.ZUORA_OMS: ZuoraOMSMCP,
        OMSProvider.NETSUITE: NetsuiteOMSMCP,
    }
    sub_types = {
        SubProvider.ORACLE_SUBSCRIPTION: OracleSubMCP,
        SubProvider.ZUORA_SUB: ZuoraSubMCP,
        SubProvider.CHARGEBEE: ChargebeeMCP,
        SubProvider.SALESFORCE_REVENUE: SalesforceRevenueMCP,
    }
    install_base_types = {
        InstallBaseProvider.ORACLE_INSTALL_BASE: OracleInstallBaseMCP,
        InstallBaseProvider.SALESFORCE_ASSET: SalesforceAssetMCP,
        InstallBaseProvider.SERVICENOW_CMDB: ServiceNowCMDBMCP,
    }
    for provider, adapter_type in crm_types.items():
        assert isinstance(MCPFactory(Settings(crm_provider=provider)).get_crm_server(), adapter_type)
    assert isinstance(MCPFactory(Settings()).get_cpq_server(), OracleCPQMCP)
    for provider, adapter_type in oms_types.items():
        assert isinstance(MCPFactory(Settings(oms_provider=provider)).get_oms_server(), adapter_type)
    for provider, adapter_type in sub_types.items():
        assert isinstance(MCPFactory(Settings(sub_provider=provider)).get_sub_server(), adapter_type)
    for provider, adapter_type in install_base_types.items():
        assert isinstance(MCPFactory(Settings(install_base_provider=provider)).get_install_base_server(), adapter_type)
