from __future__ import annotations

from context.models import Completeness


class ContextValidator:
    def validate(self, missing_sources: list[str]) -> Completeness:
        if len(missing_sources) >= 2:
            return Completeness.DEGRADED
        if missing_sources:
            return Completeness.PARTIAL
        return Completeness.COMPLETE
