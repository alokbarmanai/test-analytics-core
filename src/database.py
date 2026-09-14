# Set up the connection using SQLAlchemy's core utilities: create_engine, sessionmaker, and the DeclarativeBase layout.
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 1. Define the local database file location
DATABASE_URL = "sqlite:///./test_analytics.db"
# 2. Create the engine (connect_args is unique to SQLite for multithreading safety)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# 3. Create a session factory for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 4. Create the Base class that all your database models will inherit from


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass
