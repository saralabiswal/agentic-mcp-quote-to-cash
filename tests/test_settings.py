# Author: Sarala Biswal
from __future__ import annotations

from api.dependencies import RuntimeSettings, Settings
from context.models import CRMProvider, InstallBaseProvider, OMSProvider, SubProvider


def test_settings_defaults_and_runtime_override() -> None:
    runtime = RuntimeSettings(Settings())
    assert runtime.current.crm_provider == CRMProvider.SALESFORCE
    updated = runtime.update(crm_provider="dynamics")
    assert updated.crm_provider == CRMProvider.DYNAMICS


def test_settings_env_override(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("CRM_PROVIDER", "oracle_crm")
    monkeypatch.setenv("OMS_PROVIDER", "sap_s4hana")
    monkeypatch.setenv("SUB_PROVIDER", "chargebee")
    monkeypatch.setenv("INSTALL_BASE_PROVIDER", "servicenow_cmdb")
    settings = Settings()
    assert settings.crm_provider == CRMProvider.ORACLE_CRM
    assert settings.oms_provider == OMSProvider.SAP_S4HANA
    assert settings.sub_provider == SubProvider.CHARGEBEE
    assert settings.install_base_provider == InstallBaseProvider.SERVICENOW_CMDB


def test_all_provider_enums_accepted() -> None:
    for crm_provider in CRMProvider:
        assert Settings(crm_provider=crm_provider).crm_provider == crm_provider
    for oms_provider in OMSProvider:
        assert Settings(oms_provider=oms_provider).oms_provider == oms_provider
    for sub_provider in SubProvider:
        assert Settings(sub_provider=sub_provider).sub_provider == sub_provider
    for install_base_provider in InstallBaseProvider:
        assert Settings(install_base_provider=install_base_provider).install_base_provider == install_base_provider
