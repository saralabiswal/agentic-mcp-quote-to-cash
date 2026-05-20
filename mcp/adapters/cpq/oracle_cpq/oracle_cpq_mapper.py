# Author: Sarala Biswal
from context.models import CanonicalProduct


def map_product(raw: dict[str, object]) -> CanonicalProduct:
    return CanonicalProduct.model_validate(raw)
