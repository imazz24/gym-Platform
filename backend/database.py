"""
Database connection and session management.

Uses PostgreSQL when it is configured and reachable; otherwise it falls back
automatically to a local SQLite file so the app runs with zero setup — no
PostgreSQL installation required. Override with the DB_BACKEND environment
variable ("sqlite" or "postgres") or SQLITE_PATH to choose the file location.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.config import config

# Base class for models (import-safe: models import this before the engine).
Base = declarative_base()


def _data_dir():
    """A per-user, writable folder for the local database file.

    Works the same whether running from source or as a packaged .exe, since it
    never writes inside the (possibly read-only) application directory.
    """
    base = (
        os.environ.get("LOCALAPPDATA")       # Windows
        or os.environ.get("XDG_DATA_HOME")   # Linux
        or os.path.expanduser("~")
    )
    path = os.path.join(base, "GymPlatform")
    os.makedirs(path, exist_ok=True)
    return path


def _sqlite_url():
    db_path = os.getenv("SQLITE_PATH") or os.path.join(_data_dir(), "powerhouse.db")
    # SQLAlchemy needs forward slashes in the URL even on Windows.
    return "sqlite:///" + db_path.replace("\\", "/")


def _make_sqlite_engine():
    url = _sqlite_url()
    eng = create_engine(
        url,
        echo=False,
        # The desktop app touches the DB from a background init thread and the
        # UI thread, so allow cross-thread use of connections.
        connect_args={"check_same_thread": False},
    )
    print(f"[DB] Using local SQLite database: {url[len('sqlite:///'):]}")
    return eng


def _make_engine():
    """Pick PostgreSQL if available, else SQLite."""
    backend = (os.getenv("DB_BACKEND") or "").strip().lower()

    if backend == "sqlite":
        return _make_sqlite_engine()

    # Try PostgreSQL (default, or forced via DB_BACKEND=postgres).
    try:
        import psycopg2  # noqa: F401  (driver must be importable)

        eng = create_engine(
            config.DATABASE_URL,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        # Verify we can actually open a connection before committing to it.
        with eng.connect():
            pass
        print(f"[DB] Using PostgreSQL at {config.POSTGRES_HOST}:{config.POSTGRES_PORT}")
        return eng
    except Exception as exc:
        if backend == "postgres":
            # User explicitly demanded PostgreSQL — don't silently downgrade.
            raise
        print(f"[DB] PostgreSQL not available ({str(exc).splitlines()[0][:80]}).")
        print("[DB] Falling back to a local SQLite database (no setup needed).")
        return _make_sqlite_engine()


# Create engine (auto-detects backend) and the session factory.
engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Get a new database session"""
    return SessionLocal()


def init_db():
    """Initialize database tables"""
    from backend.models import (
        SystemUser, Member, MemberActivity, Product,
        Purchase, Payment, Expense, EmployeeLog
    )
    Base.metadata.create_all(bind=engine)

    # Run seed data
    from backend.seed import seed_data
    seed_data()


def get_db():
    """Generator for dependency injection (FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
