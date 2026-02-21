"""Pydantic domain models shared across backend and frontend layers."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Thought(BaseModel):
    """A single user thought that becomes a node in the knowledge graph."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    cluster: str | None = None


class Connection(BaseModel):
    """A directed edge between two thoughts describing their relationship."""

    source_id: str
    target_id: str
    relationship: str


class Cluster(BaseModel):
    """A named group of related thought IDs produced by AI clustering."""

    name: str
    thought_ids: list[str]


class DuplicateCheck(BaseModel):
    """Result of an AI duplicate-detection check for a new thought."""

    is_duplicate: bool
    similar_to: str | None = None
    reason: str | None = None


class PendingDuplicate(BaseModel):
    """A thought awaiting user resolution after being flagged as a duplicate."""

    text: str
    similar_to: str | None = None
    reason: str | None = None


class ProjectMeta(BaseModel):
    """Lightweight metadata for a saved project (persisted by ProjectStore)."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
