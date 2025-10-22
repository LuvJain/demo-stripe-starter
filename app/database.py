"""Database configuration for SQLAlchemy and SQLModel"""
import os
from sqlmodel import SQLModel, create_engine, Session

# Get database URL from environment variable or use default SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stripe_demo.db")

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create database and tables from SQLModel metadata"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session