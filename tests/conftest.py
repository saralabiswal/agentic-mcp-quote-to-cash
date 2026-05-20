# Author: Sarala Biswal
"""Tests for conftest behavior."""
from __future__ import annotations

import pytest

from api.dependencies import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()
