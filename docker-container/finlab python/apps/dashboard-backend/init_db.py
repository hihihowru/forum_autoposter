"""
Database initialization script.
Run this script to create all necessary database tables.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent.absolute()))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models to ensure they're registered with SQLAlchemy
from src.models.posting_models import Base
from src.main import get_db_engine

def init_db():
    """Initialize the database by creating all tables."""
    try:
        # Get the database engine
        engine = get_db_engine()
        
        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting database initialization...")
    if init_db():
        print("✅ Database initialization completed successfully!")
    else:
        print("❌ Database initialization failed!")
        sys.exit(1)
