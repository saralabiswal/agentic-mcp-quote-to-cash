# Author: Sarala Biswal
"""Completeness validator for classifying assembled context quality."""
from __future__ import annotations

from context.models import Completeness


class ContextValidator:
    """Classify context quality from missing business-source categories."""

    def validate(self, missing_sources: list[str]) -> Completeness:
        """Return complete, partial, or degraded based on missing-source count."""
        if len(missing_sources) >= 2:
            return Completeness.DEGRADED
        if missing_sources:
            return Completeness.PARTIAL
        return Completeness.COMPLETE
