"""Database configuration and session management"""
import os
from sqlmodel import create_engine, SQLModel, Session

# Get database URL from environment or use a default SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stripe_demo.db")

# Create engine with echo for development (set to False in production)
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session