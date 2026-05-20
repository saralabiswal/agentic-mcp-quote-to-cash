from __future__ import annotations

from fastapi import APIRouter

from demo.runner import DemoRunner

router = APIRouter()


@router.post("/demo/{scenario}")
async def run_demo(scenario: int) -> dict[str, object]:
    return await DemoRunner().run(scenario)
