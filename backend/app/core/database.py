"""
Database Layer for GreenAgent OS
Provides storage for workloads, telemetry traces, cache, decisions, and audit logs.
Uses SQLite for zero-configuration local-first execution.
"""
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone
import json
from typing import Generator

DATABASE_URL = "sqlite:///./greenagent.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class WorkloadDB(Base):
    __tablename__ = "workloads"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    prompt = Column(Text)
    system_prompt = Column(Text, nullable=True)
    expected_output_format = Column(String, default="text")
    priority = Column(String, default="NORMAL")
    deadline_seconds = Column(Float, default=60.0)
    user_blocking = Column(Boolean, default=False)
    safety_sensitive = Column(Boolean, default=False)
    allow_cache = Column(Boolean, default=True)
    allow_delay = Column(Boolean, default=True)
    allow_region_shift = Column(Boolean, default=True)
    preferred_region = Column(String, default="us-east")
    required_quality_min = Column(Float, default=0.85)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ExecutionTraceDB(Base):
    __tablename__ = "execution_traces"

    id = Column(String, primary_key=True, index=True)
    workload_id = Column(String, index=True)
    model = Column(String, index=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    retries = Column(Integer, default=0)
    tool_calls_count = Column(Integer, default=0)
    tool_calls_latency_ms = Column(Float, default=0.0)
    cache_hit = Column(Boolean, default=False)
    status = Column(String, default="COMPLETED")
    raw_response = Column(Text, nullable=True)
    energy_joules = Column(Float, default=0.0)
    carbon_co2e_grams = Column(Float, default=0.0)
    measurement_method = Column(String, default="estimated_energy")
    details_json = Column(Text, default="{}")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CacheEntryDB(Base):
    __tablename__ = "cache_entries"

    id = Column(String, primary_key=True, index=True)
    key_hash = Column(String, index=True, unique=True)
    prompt = Column(Text)
    response = Column(Text)
    model = Column(String)
    tokens_saved = Column(Integer, default=0)
    energy_saved_joules = Column(Float, default=0.0)
    carbon_saved_grams = Column(Float, default=0.0)
    ttl_seconds = Column(Integer, default=86400)
    expires_at = Column(DateTime)
    hit_count = Column(Integer, default=0)
    safety_tier = Column(String, default="general")
    embedding_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLogDB(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    actor = Column(String)
    action = Column(String)
    resource_type = Column(String)
    resource_id = Column(String)
    details_json = Column(Text, default="{}")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
