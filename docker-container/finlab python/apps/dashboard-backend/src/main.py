"""
發文管理系統後端主應用
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

# 加載環境變量
env_path = Path('.') / '.env'
load_dotenv(env_path)

# 導入API路由
from src.api.posting_management import router as posting_router

# 數據庫配置 - 處理 Railway 的 DATABASE_URL 格式
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/posting_management")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 創建FastAPI應用
app = FastAPI(
    title="發文管理系統API",
    description="發文管理系統後端API服務",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 數據庫引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 導入模型以確保它們被註冊
from src.models.posting_models import Base

# 創建數據庫表
try:
    print("🔄 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
except Exception as e:
    print(f"❌ Error creating database tables: {e}")
    raise

# 依賴注入函數
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 註冊路由
app.include_router(posting_router, prefix="/api/posting-management", tags=["發文管理"])

@app.get("/")
async def root():
    return {"message": "發文管理系統API服務運行中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服務正常運行"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
