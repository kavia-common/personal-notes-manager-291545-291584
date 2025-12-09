import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text

from .db import Base


def utcnow() -> datetime:
    """Current UTC time without tzinfo for SQLite compatibility."""
    return datetime.utcnow()


class NoteORM(Base):
    """SQLAlchemy ORM model for a Note."""
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # Store tags as a comma-separated string for SQLite simplicity; expose as list via schema transformations in API
    tags_raw: Mapped[Optional[str]] = mapped_column("tags", Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Helper methods to convert tags list <-> stored string
    @staticmethod
    def tags_to_raw(tags: Optional[List[str]]) -> Optional[str]:
        if tags is None:
            return None
        # Normalize: strip spaces and ignore empties
        normalized = [t.strip() for t in tags if t and t.strip()]
        return ",".join(normalized) if normalized else None

    @staticmethod
    def raw_to_tags(raw: Optional[str]) -> list[str]:
        if not raw:
            return []
        parts = [p.strip() for p in raw.split(",")]
        return [p for p in parts if p]
