from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from context.models import ConflictResolution


@dataclass(frozen=True)
class ConflictResolver:
    def resolve(self, context_parts: dict[str, Any]) -> tuple[dict[str, Any], list[ConflictResolution]]:
        resolutions: list[ConflictResolution] = []
        self._resolve_account_value(context_parts, resolutions)
        self._resolve_renewal_date(context_parts, resolutions)
        account = context_parts.get("account")
        installed_base = context_parts.get("installed_base")
        if account is not None and installed_base is not None:
            context_parts["account"] = account.model_copy(update={"installed_base": installed_base})
            resolutions.append(
                ConflictResolution(
                    field_path="account.installed_base",
                    winning_source="install_base",
                    losing_sources=["crm"],
                    rule_applied="install_base_enrichment",
                    chosen_value=len(installed_base),
                )
            )
        return context_parts, resolutions

    def _resolve_account_value(
        self,
        context_parts: dict[str, Any],
        resolutions: list[ConflictResolution],
    ) -> None:
        candidates = context_parts.get("account_candidates")
        if not candidates:
            return
        typed_candidates = list(candidates)
        winner_source, winner = max(
            typed_candidates,
            key=lambda item: item[1].account_value,
        )
        context_parts["account"] = winner
        resolutions.append(
            ConflictResolution(
                field_path="account.account_value",
                winning_source=str(winner_source),
                losing_sources=[str(source) for source, _account in typed_candidates if source != winner_source],
                rule_applied="higher_value_wins",
                chosen_value=Decimal(winner.account_value),
            )
        )

    def _resolve_renewal_date(
        self,
        context_parts: dict[str, Any],
        resolutions: list[ConflictResolution],
    ) -> None:
        subscription = context_parts.get("subscription")
        opportunity = context_parts.get("opportunity")
        if subscription is None or opportunity is None:
            return
        resolutions.append(
            ConflictResolution(
                field_path="subscription.renewal_date",
                winning_source="subscription",
                losing_sources=["crm_opportunity"],
                rule_applied="subscription_system_authoritative",
                chosen_value=subscription.renewal_date,
            )
        )
