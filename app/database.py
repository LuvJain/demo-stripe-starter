"""Database connection and session management"""
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Get database URL from environment or use SQLite in-memory for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stripe_demo.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)


def create_db_and_tables():
    """Create database tables from SQLModel models"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting a database session"""
    with Session(engine) as session:
        yield session