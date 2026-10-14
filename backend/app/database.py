"""
Database configuration and session management.

This module sets up the SQLAlchemy engine, session factory, and base class
for ORM models. It also provides the get_db dependency for FastAPI route handlers.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment, with fallback to SQLite default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leadflow.db")

# Create SQLAlchemy engine
# check_same_thread=False is required for SQLite when using FastAPI
# (SQLite default is to enforce single-thread access, but FastAPI uses thread pools)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
# autocommit=False: changes must be explicitly committed
# autoflush=False: prevents automatic flushes before queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session.

    Yields a session and ensures it is closed after the request completes,
    even if an exception occurs.

    Usage in route handlers:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
