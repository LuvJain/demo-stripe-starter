"""Database connection and session management"""
import os
from sqlmodel import SQLModel, create_engine, Session

# Get database URL from environment or use default SQLite URL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./stripe_demo.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Initialize database and create tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session