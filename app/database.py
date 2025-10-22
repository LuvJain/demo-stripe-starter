"""Database configuration for the application"""
import os
from sqlmodel import SQLModel, create_engine, Session

# SQLite database URL for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stripe_demo.db")

# Create SQLModel engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Only needed for SQLite
    echo=bool(os.getenv("SQL_ECHO", "False").lower() == "true")
)


def create_db_and_tables():
    """Create database tables from SQLModel metadata"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session