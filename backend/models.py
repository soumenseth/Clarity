from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Thought(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    cluster: str | None = None


class Connection(BaseModel):
    source_id: str
    target_id: str
    relationship: str


class Cluster(BaseModel):
    name: str
    thought_ids: list[str]


class DuplicateCheck(BaseModel):
    is_duplicate: bool
    similar_to: str | None = None
    reason: str | None = None


class PendingDuplicate(BaseModel):
    text: str
    similar_to: str | None = None
    reason: str | None = None
