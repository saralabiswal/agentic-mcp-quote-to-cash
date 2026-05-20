FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_MODE=demo

COPY pyproject.toml README.md ./
COPY api api
COPY mcp mcp
COPY context context
COPY agents agents
COPY audit audit
COPY demo demo
COPY seed_data seed_data

RUN pip install --no-cache-dir -e .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
