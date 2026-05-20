from __future__ import annotations

from functools import lru_cache
from typing import Self

from pydantic_settings import BaseSettings, SettingsConfigDict

from context.models import AppMode, CRMProvider, InstallBaseProvider, OMSProvider, SubProvider


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    crm_provider: CRMProvider = CRMProvider.SALESFORCE
    oms_provider: OMSProvider = OMSProvider.ORACLE_FOM
    sub_provider: SubProvider = SubProvider.ORACLE_SUBSCRIPTION
    install_base_provider: InstallBaseProvider = InstallBaseProvider.ORACLE_INSTALL_BASE
    install_base_enabled: bool = True
    app_mode: AppMode = AppMode.DEMO
    mcp_timeout_seconds: int = 5
    context_assembly_timeout_seconds: int = 10
    database_url: str = "sqlite+aiosqlite:///./audit.db"
    sf_instance_url: str = ""
    sf_client_id: str = ""
    sf_client_secret: str = ""
    sf_token_url: str = ""
    dynamics_tenant_id: str = ""
    dynamics_client_id: str = ""
    dynamics_client_secret: str = ""
    dynamics_org_url: str = ""
    oracle_crm_base_url: str = ""
    oracle_crm_username: str = ""
    oracle_crm_password: str = ""
    oracle_cpq_base_url: str = ""
    oracle_cpq_api_key: str = ""
    oracle_fom_oic_url: str = ""
    oracle_fom_username: str = ""
    oracle_fom_password: str = ""
    oracle_sub_oic_url: str = ""
    oracle_sub_username: str = ""
    oracle_sub_password: str = ""
    oracle_ib_base_url: str = ""
    oracle_ib_api_key: str = ""
    salesforce_asset_instance_url: str = ""
    salesforce_asset_client_id: str = ""
    salesforce_asset_client_secret: str = ""
    servicenow_cmdb_base_url: str = ""
    servicenow_cmdb_username: str = ""
    servicenow_cmdb_password: str = ""
    salesforce_oms_instance_url: str = ""
    salesforce_revenue_instance_url: str = ""
    sap_host: str = ""
    sap_client: str = ""
    sap_username: str = ""
    sap_password: str = ""
    zuora_base_url: str = ""
    zuora_client_id: str = ""
    zuora_client_secret: str = ""
    netsuite_account_id: str = ""
    netsuite_consumer_key: str = ""
    netsuite_consumer_secret: str = ""
    netsuite_token_id: str = ""
    netsuite_token_secret: str = ""
    chargebee_site: str = ""
    chargebee_api_key: str = ""
    min_margin_floor: float = 0.18
    approval_discount_threshold: float = 0.10

    def with_overrides(self, **overrides: object) -> Self:
        data = self.model_dump()
        data.update(overrides)
        return self.__class__.model_validate(data)


class RuntimeSettings:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def current(self) -> Settings:
        return self._settings

    def update(self, **overrides: object) -> Settings:
        self._settings = self._settings.with_overrides(**overrides)
        return self._settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(get_settings())
