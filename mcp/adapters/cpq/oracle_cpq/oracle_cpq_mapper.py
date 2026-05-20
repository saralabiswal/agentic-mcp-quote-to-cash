# Author: Sarala Biswal
"""Canonical mapper exports for the Oracle Cpq adapter package."""
from context.models import CanonicalProduct


def map_product(raw: dict[str, object]) -> CanonicalProduct:
    return CanonicalProduct.model_validate(raw)
