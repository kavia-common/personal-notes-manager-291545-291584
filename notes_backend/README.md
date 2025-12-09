# Notes Backend (FastAPI)

FastAPI service providing CRUD endpoints for personal notes with SQLite persistence.

## Quick Start

1. Install dependencies (Python 3.10+ recommended):
   pip install -r requirements.txt

2. Run the app (binds on 0.0.0.0:3001):
   uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

3. Open API docs:
   http://localhost:3001/docs

## Environment Variables (optional)

- DATABASE_URL: Full SQLAlchemy URL for the database. Example: sqlite:///notes.db
- SQLITE_PATH: If DATABASE_URL not set, path to SQLite file (default: notes.db)

A local SQLite file will be used by default (no external services required).

## Endpoints

- GET /health — health check
- POST /notes — create a new note
- GET /notes — list notes with optional pagination and filters
  - Query params: search, tag, limit, offset
- GET /notes/{id} — get a note by id
- PUT /notes/{id} — update a note
- DELETE /notes/{id} — delete a note

List response includes pagination metadata:
{
  "items": [...],
  "total": 0,
  "limit": 20,
  "offset": 0
}

## Data Model

Note:
- id (uuid string)
- title (1..200 chars)
- content (string)
- tags (list[string])
- created_at (datetime)
- updated_at (datetime)
- pinned (bool)
- archived (bool)

## Development Notes

- CORS is permissive for local development.
- SQLite-backed via SQLAlchemy; tables auto-created on startup.
- OpenAPI docs include tags and schemas.
