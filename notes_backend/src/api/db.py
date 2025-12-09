import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# Load environment variables if available (optional dependency is already in requirements)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # It's fine if python-dotenv is not available at runtime
    pass


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


def get_database_url() -> str:
    """
    Resolve the database URL from environment or fallback to a local SQLite file.
    Env vars:
      - DATABASE_URL: Preferred full SQLAlchemy URL.
      - SQLITE_PATH: Optional path to a sqlite file (used if DATABASE_URL not set).
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    sqlite_path = os.getenv("SQLITE_PATH", "notes.db")
    # Ensure folder exists if a path with directories is provided
    directory = os.path.dirname(sqlite_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return f"sqlite:///{sqlite_path}"


DATABASE_URL = get_database_url()

# For SQLite, need check_same_thread=False for multi-threaded FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session, future=True)


def init_db() -> None:
    """Create tables if they don't exist. Called on startup."""
    # Import models here to register mappings
    from .models import NoteORM  # noqa: F401
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.
    Commits on success and rolls back on error.
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
