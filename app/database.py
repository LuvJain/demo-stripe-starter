"""Database connection and session management"""
from sqlmodel import SQLModel, create_engine, Session

# SQLite in-memory database for this demo
# In production, use a proper DB connection string with environment variables
DATABASE_URL = "sqlite:///./stripe_demo.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """Create all tables defined in SQLModel models"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a new database session"""
    with Session(engine) as session:
        yield session