from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .db import init_db, session_scope
from .models import NoteORM
from .schemas import NoteCreate, NoteUpdate, NoteRead, PaginatedNotes

app = FastAPI(
    title="Personal Notes API",
    description="A simple FastAPI service to manage personal notes with CRUD operations.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Service health and status endpoints."},
        {"name": "Notes", "description": "CRUD operations for managing notes."},
    ],
)

# CORS: permissive for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local preview/dev; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database on startup."""
    init_db()


# PUBLIC_INTERFACE
@app.get("/health", tags=["Health"], summary="Health Check", description="Simple service healthcheck returning status.")
def health_check():
    """Return basic health info."""
    return {"status": "ok"}


def orm_to_read(note: NoteORM) -> NoteRead:
    """Convert ORM object to NoteRead schema."""
    return NoteRead(
        id=note.id,
        title=note.title,
        content=note.content,
        tags=NoteORM.raw_to_tags(note.tags_raw),
        created_at=note.created_at,
        updated_at=note.updated_at,
        pinned=note.pinned,
        archived=note.archived,
    )


# PUBLIC_INTERFACE
@app.post(
    "/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Notes"],
    summary="Create a note",
    description="Create a new note with title, content, tags, and flags.",
)
def create_note(payload: NoteCreate):
    """Create a new note and return it."""
    now = datetime.utcnow()
    with session_scope() as session:
        db_note = NoteORM(
            title=payload.title,
            content=payload.content or "",
            tags_raw=NoteORM.tags_to_raw(payload.tags),
            created_at=now,
            updated_at=now,
            pinned=payload.pinned,
            archived=payload.archived,
        )
        session.add(db_note)
        session.flush()  # Ensure ID is populated
        return orm_to_read(db_note)


# PUBLIC_INTERFACE
@app.get(
    "/notes",
    response_model=PaginatedNotes,
    tags=["Notes"],
    summary="List notes",
    description="List notes with optional search by title/content and filter by tag. Supports pagination via limit and offset.",
)
def list_notes(
    search: Optional[str] = Query(default=None, description="Search text in title or content."),
    tag: Optional[str] = Query(default=None, description="Filter by a single tag."),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of notes to return."),
    offset: int = Query(default=0, ge=0, description="Number of notes to skip."),
):
    """List notes with pagination and optional filters."""
    with session_scope() as session:
        stmt = select(NoteORM)
        count_stmt = select(func.count())

        if search:
            like = f"%{search}%"
            stmt = stmt.where((NoteORM.title.like(like)) | (NoteORM.content.like(like)))
            count_stmt = count_stmt.select_from(NoteORM).where((NoteORM.title.like(like)) | (NoteORM.content.like(like)))
        else:
            count_stmt = count_stmt.select_from(NoteORM)

        if tag:
            # Simple LIKE match on tags_raw; ensures tag matches as full token separated by commas.
            token = f"%{tag}%"
            stmt = stmt.where(NoteORM.tags_raw.like(token))
            count_stmt = count_stmt.where(NoteORM.tags_raw.like(token))

        total = session.execute(count_stmt).scalar_one()
        items = session.execute(stmt.order_by(NoteORM.created_at.desc()).limit(limit).offset(offset)).scalars().all()

        return PaginatedNotes(
            items=[orm_to_read(n) for n in items],
            total=total,
            limit=limit,
            offset=offset,
        )


# PUBLIC_INTERFACE
@app.get(
    "/notes/{note_id}",
    response_model=NoteRead,
    tags=["Notes"],
    summary="Get a note",
    description="Fetch a note by its UUID.",
)
def get_note(note_id: str):
    """Retrieve a note by ID."""
    with session_scope() as session:
        note = _get_note_or_404(session, note_id)
        return orm_to_read(note)


# PUBLIC_INTERFACE
@app.put(
    "/notes/{note_id}",
    response_model=NoteRead,
    tags=["Notes"],
    summary="Update a note",
    description="Update fields of a note by its UUID.",
)
def update_note(note_id: str, payload: NoteUpdate):
    """Update a note by ID."""
    with session_scope() as session:
        note = _get_note_or_404(session, note_id)

        if payload.title is not None:
            note.title = payload.title
        if payload.content is not None:
            note.content = payload.content
        if payload.tags is not None:
            note.tags_raw = NoteORM.tags_to_raw(payload.tags)
        if payload.pinned is not None:
            note.pinned = payload.pinned
        if payload.archived is not None:
            note.archived = payload.archived

        note.updated_at = datetime.utcnow()
        session.add(note)
        session.flush()
        return orm_to_read(note)


# PUBLIC_INTERFACE
@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Notes"],
    summary="Delete a note",
    description="Delete a note by its UUID. Returns 204 on success.",
)
def delete_note(note_id: str):
    """Delete a note and return no content."""
    with session_scope() as session:
        note = _get_note_or_404(session, note_id)
        session.delete(note)
        # session_scope commits on exit
        return None


def _get_note_or_404(session: Session, note_id: str) -> NoteORM:
    """Helper to fetch a note or raise 404."""
    note = session.get(NoteORM, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note
