# Author: Sarala Biswal
"""Demo API router for executing curated quote-to-cash scenarios."""
from __future__ import annotations

from fastapi import APIRouter

from demo.runner import DemoRunner

router = APIRouter()


@router.post("/demo/{scenario}")
async def run_demo(scenario: int) -> dict[str, object]:
    """Execute one of the curated demo scenarios through the backend flow."""
    return await DemoRunner().run(scenario)
