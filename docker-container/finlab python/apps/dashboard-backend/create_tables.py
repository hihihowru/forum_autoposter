"""
Script to create all database tables.
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models to ensure they're registered with SQLAlchemy
from src.models.posting_models import Base

def create_tables():
    """Create all database tables."""
    try:
        # Get database URL from environment variables
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL environment variable not set")
            return False
            
        print(f"Connecting to database: {db_url}")
        
        # Create engine and session
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
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
    print("Starting database table creation...")
    if create_tables():
        print("✅ Database table creation completed successfully!")
    else:
        print("❌ Database table creation failed!")
        sys.exit(1)
