# Author: Sarala Biswal
"""SQLAlchemy table models for context, conflict, source-call, and agent-run audit records."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ContextRunRecord(Base):
    __tablename__ = "context_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context_run_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    assembled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(JSON)


class ConflictRecord(Base):
    __tablename__ = "conflict_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context_run_id: Mapped[str] = mapped_column(String(80), index=True)
    field_path: Mapped[str] = mapped_column(String(200))
    payload: Mapped[dict[str, object]] = mapped_column(JSON)


class AgentRunRecord(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context_run_id: Mapped[str] = mapped_column(String(80), index=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(JSON)


class SourceCallRecord(Base):
    __tablename__ = "source_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context_run_id: Mapped[str] = mapped_column(String(80), index=True)
    source: Mapped[str] = mapped_column(String(80))
    latency_ms: Mapped[int] = mapped_column(Integer)
    success: Mapped[bool]
