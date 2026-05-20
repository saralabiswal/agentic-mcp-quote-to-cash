# Author: Sarala Biswal
from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def test_api_happy_paths() -> None:
    with TestClient(app) as client:
        assert client.get("/settings").status_code == 200
        response = client.post("/context/assemble", json={"account_id": "ACC-001"})
        assert response.status_code == 200
        context_run_id = response.json()["context_run_id"]
        assert response.json()["account"]["canonical_account_id"] == "ACC-001"
        assert client.get(f"/context/{context_run_id}").status_code == 200
        assert client.post("/context/compare", json={"account_id": "ACC-001"}).status_code == 200

        response = client.post("/agent/run", json={"account_id": "ACC-001"})
        assert response.status_code == 200
        assert response.json()["risk_tier"] == "high"
        assert client.get("/agent/runs").json()
        assert client.get(f"/audit/{response.json()['context_run_id']}").status_code == 200

        assert client.post("/settings", json={"crm_provider": "dynamics"}).status_code == 200
        readiness = client.get("/readiness")
        assert readiness.status_code == 200
        assert len(readiness.json()) == 16
        assert client.post("/demo/1").status_code == 200


def test_api_error_paths() -> None:
    with TestClient(app) as client:
        assert client.get("/context/NOPE").status_code == 404
        assert client.get("/audit/NOPE").status_code == 404
