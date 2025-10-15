"""
數據庫配置和依賴注入
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 數據庫配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/posting_management"
)

# 創建數據庫引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """數據庫會話依賴注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
