PYTHON ?= uv run python

.PHONY: install seed dev-api dev-ui demo demo-all test lint docker-up clean

install:
	uv sync --python 3.12 --extra dev

seed:
	$(PYTHON) -m seed_data.seeder

dev-api:
	uv run uvicorn api.main:app --reload --port 8000

dev-ui:
	cd ui && npm run dev

demo:
	$(PYTHON) -m demo.runner 1

demo-all:
	$(PYTHON) -m demo.runner all

test:
	uv run pytest --cov=. --cov-fail-under=80

lint:
	uv run ruff check .
	uv run mypy --strict context agents api mcp

docker-up:
	docker compose up --build -d

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage audit.db
