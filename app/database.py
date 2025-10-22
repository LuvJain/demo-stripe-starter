"""Database configuration and utility functions"""
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use a default SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stripe_demo.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create database tables if they don't exist"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a new database session"""
    with Session(engine) as session:
        yield session