<!-- Author: Sarala Biswal -->
# Architecture

This implementation follows the planning architecture:

- MCP adapter layer with 16 selectable adapters.
- Context assembly with concurrent `asyncio.gather(..., return_exceptions=True)`.
- Frozen Pydantic v2 canonical schema.
- Deterministic renewal signal and decision agents.
- FastAPI endpoints for context, agent, audit, demo, settings, and readiness.
