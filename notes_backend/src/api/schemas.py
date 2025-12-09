from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, constr


# PUBLIC_INTERFACE
class NoteCreate(BaseModel):
    """Schema for creating a new note."""
    title: constr(min_length=1, max_length=200) = Field(..., description="Title of the note (1..200 chars).")
    content: str = Field("", description="Content/body of the note.")
    tags: Optional[List[str]] = Field(default=None, description="Optional list of tags for the note.")
    pinned: bool = Field(default=False, description="Whether the note is pinned.")
    archived: bool = Field(default=False, description="Whether the note is archived.")


# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Schema for updating an existing note (all fields optional)."""
    title: Optional[constr(min_length=1, max_length=200)] = Field(default=None, description="Updated title.")
    content: Optional[str] = Field(default=None, description="Updated content.")
    tags: Optional[List[str]] = Field(default=None, description="Replace tags with provided list.")
    pinned: Optional[bool] = Field(default=None, description="Set pinned flag.")
    archived: Optional[bool] = Field(default=None, description="Set archived flag.")


# PUBLIC_INTERFACE
class NoteRead(BaseModel):
    """Schema for reading a note."""
    id: str = Field(..., description="Note UUID identifier.")
    title: str = Field(..., description="Title of the note.")
    content: str = Field(..., description="Content of the note.")
    tags: list[str] = Field(default_factory=list, description="List of tags for the note.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC).")
    pinned: bool = Field(..., description="Whether the note is pinned.")
    archived: bool = Field(..., description="Whether the note is archived.")


# PUBLIC_INTERFACE
class PaginatedNotes(BaseModel):
    """Paginated response for notes listing."""
    items: list[NoteRead] = Field(..., description="List of notes in this page.")
    total: int = Field(..., description="Total number of notes matching filters.")
    limit: int = Field(..., description="Page size limit.")
    offset: int = Field(..., description="Offset applied.")
