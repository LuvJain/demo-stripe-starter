"""Database configuration for SQLModel and connection management"""
import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# Use environment variable for database URL or fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stripe_demo.db")

# Create engine for database connection
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """Create database tables from SQLModel models"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session