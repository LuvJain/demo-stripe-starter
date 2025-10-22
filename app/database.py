"""Database configuration and utilities"""
import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# SQLite database URL for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stripe_app.db")

# Create engine with reasonable defaults
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)


def create_db_and_tables():
    """Create all database tables if they don't exist"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting a database session"""
    with Session(engine) as session:
        yield session