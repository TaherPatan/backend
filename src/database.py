from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .config import settings
import os

# Database connection URL
DATABASE_URL = settings.database_url

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create database tables
def create_db_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # Example usage: create tables if the script is run directly
    print("Creating database tables...")
    create_db_tables()
    print("Database tables created.")
# Roo temp change 5