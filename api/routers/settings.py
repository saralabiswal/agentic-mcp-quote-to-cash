from __future__ import annotations

from time import perf_counter
from typing import Any

from fastapi import APIRouter

from api.dependencies import get_runtime_settings
from context.models import CRMProvider, InstallBaseProvider, OMSProvider, SubProvider
from mcp.factory import MCPFactory

router = APIRouter()


@router.get("/settings")
async def get_settings() -> dict[str, Any]:
    return get_runtime_settings().current.model_dump(mode="json")


@router.post("/settings")
async def update_settings(payload: dict[str, Any]) -> dict[str, Any]:
    return get_runtime_settings().update(**payload).model_dump(mode="json")


@router.get("/readiness")
async def readiness() -> list[dict[str, object]]:
    runtime = get_runtime_settings().current
    checks: list[tuple[str, str, Any]] = []
    for crm_provider in CRMProvider:
        settings = runtime.with_overrides(crm_provider=crm_provider)
        checks.append((f"{crm_provider.value}_mcp.py", crm_provider.value, MCPFactory(settings).get_crm_server().get_account("ACC-001")))
    checks.append(("oracle_cpq_mcp.py", "oracle_cpq", MCPFactory(runtime).get_cpq_server().get_product_catalog("enterprise")))
    for oms_provider in OMSProvider:
        settings = runtime.with_overrides(oms_provider=oms_provider)
        checks.append((f"{oms_provider.value}_mcp.py", oms_provider.value, MCPFactory(settings).get_oms_server().get_orders("ACC-001")))
    for sub_provider in SubProvider:
        settings = runtime.with_overrides(sub_provider=sub_provider)
        checks.append((f"{sub_provider.value}_mcp.py", sub_provider.value, MCPFactory(settings).get_sub_server().get_subscription("ACC-001")))
    install_files = {
        InstallBaseProvider.ORACLE_INSTALL_BASE: "oracle_install_base_mcp.py",
        InstallBaseProvider.SALESFORCE_ASSET: "salesforce_asset_mcp.py",
        InstallBaseProvider.SERVICENOW_CMDB: "servicenow_cmdb_mcp.py",
    }
    for install_base_provider in InstallBaseProvider:
        settings = runtime.with_overrides(install_base_provider=install_base_provider)
        checks.append(
            (
                install_files[install_base_provider],
                install_base_provider.value,
                MCPFactory(settings).get_install_base_server().get_installed_products("ACC-001"),
            )
        )

    results: list[dict[str, object]] = []
    for name, provider, call in checks:
        started = perf_counter()
        try:
            await call
            status = "green"
        except Exception:
            status = "red"
        results.append(
            {
                "name": name,
                "provider": provider,
                "mode": runtime.app_mode.value,
                "status": status,
                "latency_ms": round((perf_counter() - started) * 1000, 2),
            }
        )
    return results
