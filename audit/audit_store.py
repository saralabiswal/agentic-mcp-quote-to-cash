# Author: Sarala Biswal
"""Async audit store that persists canonical context runs and agent decisions."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from agents.decision_agent import AgentDecision
from audit.models import AgentRunRecord, Base, ContextRunRecord
from context.models import UnifiedContext


class AuditStore:
    """Async repository for canonical context and decision audit records."""

    def __init__(self, database_url: str) -> None:
        """Create an async SQLAlchemy engine and session factory."""
        self.engine: AsyncEngine = create_async_engine(database_url)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init(self) -> None:
        """Create audit tables if they do not already exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_context_run(self, context: UnifiedContext) -> None:
        """Persist a serialized `UnifiedContext` payload."""
        async with self.session_factory() as session:
            session.add(
                ContextRunRecord(
                    context_run_id=context.context_run_id,
                    account_id=context.account.canonical_account_id,
                    assembled_at=context.assembled_at,
                    payload=context.model_dump(mode="json"),
                )
            )
            await session.commit()

    async def save_agent_run(self, decision: AgentDecision) -> None:
        """Persist a serialized agent decision payload."""
        async with self.session_factory() as session:
            session.add(
                AgentRunRecord(
                    context_run_id=decision.context_run_id,
                    account_id=decision.account_id,
                    created_at=decision.created_at,
                    payload=decision.model_dump(mode="json"),
                )
            )
            await session.commit()

    async def get_context_run(self, context_run_id: str) -> UnifiedContext | None:
        """Load a context run and rehydrate it as a frozen canonical model."""
        async with self.session_factory() as session:
            record = await session.scalar(
                select(ContextRunRecord).where(ContextRunRecord.context_run_id == context_run_id)
            )
            return UnifiedContext.model_validate(record.payload) if record else None

    async def get_agent_runs(self) -> list[dict[str, object]]:
        """Return stored decision payloads newest first for the audit UI."""
        async with self.session_factory() as session:
            records = await session.scalars(select(AgentRunRecord).order_by(AgentRunRecord.id.desc()))
            return [record.payload for record in records]


async def init_store(database_url: str) -> AuditStore:
    """Initialize and return an audit store for startup helpers or tests."""
    store = AuditStore(database_url)
    await store.init()
    return store
