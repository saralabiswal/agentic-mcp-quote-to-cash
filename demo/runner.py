# Author: Sarala Biswal
"""Command-line and API-backed runner for the seven demo scenarios."""
from __future__ import annotations

import asyncio
import sys
from typing import Any

from agents.decision_agent import DecisionAgent
from api.dependencies import Settings
from context.assembler import ContextAssembler
from context.models import Completeness, CRMProvider, OMSProvider, SubProvider


class DemoRunner:
    async def run(self, scenario: int) -> dict[str, Any]:
        settings = self._settings_for(scenario)
        account_id = {
            1: "ACC-001",
            2: "ACC-002",
            3: "ACC-002",
            4: "ACC-003",
            5: "ACC-001",
            6: "ACC-003",
            7: "ACC-004",
        }[scenario]
        context = await ContextAssembler(settings).assemble(account_id)
        if scenario == 6:
            context = context.model_copy(
                update={
                    "context_completeness": Completeness.PARTIAL,
                    "missing_sources": ["subscription"],
                }
            )
        decision = DecisionAgent(
            min_margin_floor=settings.min_margin_floor,
            approval_discount_threshold=settings.approval_discount_threshold,
        ).decide(context)
        result = {
            "scenario": scenario,
            "account_id": account_id,
            "context_completeness": context.context_completeness.value,
            "risk_tier": decision.risk_tier.value,
            "recommended_action": decision.recommended_action.value,
            "adjusted_price": str(decision.adjusted_price),
            "decision_flag": decision.decision_flag,
        }
        if scenario == 1:
            result["snapshot_vs_live"] = {
                "snapshot": {"risk_tier": "medium", "recommended_action": "risk_adjusted_renewal"},
                "live": {"risk_tier": decision.risk_tier.value, "recommended_action": decision.recommended_action.value},
            }
        return result

    def _settings_for(self, scenario: int) -> Settings:
        if scenario == 3:
            return Settings(crm_provider=CRMProvider.DYNAMICS)
        if scenario == 4:
            return Settings(crm_provider=CRMProvider.ORACLE_CRM, oms_provider=OMSProvider.SAP_S4HANA, sub_provider=SubProvider.ZUORA_SUB)
        if scenario == 5:
            return Settings(oms_provider=OMSProvider.ZUORA_OMS, sub_provider=SubProvider.CHARGEBEE)
        return Settings()


async def _main(argv: list[str]) -> None:
    runner = DemoRunner()
    scenarios = range(1, 8) if len(argv) > 1 and argv[1] == "all" else [int(argv[1]) if len(argv) > 1 else 1]
    for scenario in scenarios:
        result = await runner.run(scenario)
        print(f"Scenario {scenario}: {result}")


if __name__ == "__main__":
    asyncio.run(_main(sys.argv))
