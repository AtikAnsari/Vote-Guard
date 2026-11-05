"""
VOTE-GUARD Database Configuration & Connection Module
Uses SQLAlchemy with PyMySQL driver for MySQL 8.0+.
Credentials are dynamically loaded from environment variables (.env).
No passwords or secrets are hardcoded.
"""

import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

# Load .env file reliably using absolute paths regardless of current working directory
backend_dir = Path(__file__).resolve().parent.parent
backend_env = backend_dir / ".env"
root_env = backend_dir.parent / ".env"

if backend_env.exists():
    load_dotenv(dotenv_path=backend_env, override=True)
elif root_env.exists():
    load_dotenv(dotenv_path=root_env, override=True)
else:
    load_dotenv(override=True)

# Read Database Configuration from Environment Variables
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "vote_guard")

# Construct MySQL connection URL safely using SQLAlchemy URL.create()
# This properly handles special characters without manual string concatenation
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT) if DB_PORT else 3306,
    database=DB_NAME,
    query={"charset": "utf8mb4"},
)

# Initialize SQLAlchemy Engine with connection health checking
# pool_pre_ping=True tests connections before handing them out
# pool_recycle=3600 prevents stale MySQL timeout drops
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 3},
    echo=os.getenv("DB_ECHO", "False").lower() in ("true", "1", "yes"),
)

# Session factory for handling transactional scopes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for future SQLAlchemy ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request.
    Ensures sessions are closed automatically when the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """
    Safely tests connectivity to MySQL Server without raising unhandled exceptions.
    Returns a status dictionary suitable for health-check reporting.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION()"))
            version_row = result.fetchone()
            version_str = version_row[0] if version_row else "Unknown"
        return {
            "status": "connected",
            "database": DB_NAME,
            "host": f"{DB_HOST}:{DB_PORT}",
            "server_version": version_str,
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "database": DB_NAME,
            "host": f"{DB_HOST}:{DB_PORT}",
            "error": str(e),
            "note": "Verify MySQL Server is running and .env credentials match.",
        }

