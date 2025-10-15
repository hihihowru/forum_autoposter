"""
發文管理系統後端主應用
"""

import logging
import sys
import traceback
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 加載環境變量
env_path = Path('.') / '.env'
load_dotenv(env_path)

# 導入API路由
from src.api.posting_management import router as posting_router

# 數據庫配置 - 處理 Railway 的 DATABASE_URL 格式
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/posting_management")
logger.info(f"Initial DATABASE_URL: {DATABASE_URL}")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info(f"Updated DATABASE_URL: {DATABASE_URL}")

# Ensure required environment variables are set
required_env_vars = ["DATABASE_URL"]
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"Required environment variable {var} is not set")
        # Don't exit here to allow the application to start and show proper error in health check

# 全局异常处理器
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# 創建FastAPI應用
app = FastAPI(
    title="發文管理系統API",
    description="發文管理系統後端API服務",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 添加全局异常处理器
app.add_exception_handler(Exception, global_exception_handler)

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # 记录请求信息
    logger.info(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {request.headers}")
    
    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        
        # 记录响应信息
        logger.info(f"Response: {response.status_code} - {request.method} {request.url} - {process_time:.4f}s")
        
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}\n{traceback.format_exc()}")
        raise

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
try:
    logger.info(f"Connecting to database with URL: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connection pool created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

# 導入模型以確保它們被註冊
from src.models.posting_models import Base

# 創建數據庫表
try:
    logger.info("🔄 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully!")
except Exception as e:
    logger.error(f"❌ Error creating database tables: {str(e)}\n{traceback.format_exc()}")
    raise

# 依賴注入函數
def get_db():
    db = None
    try:
        db = SessionLocal()
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Error getting database session: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
    finally:
        if db is not None:
            db.close()
            logger.debug("Database session closed")

# 註冊路由
app.include_router(posting_router, prefix="/api/posting-management", tags=["發文管理"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "發文管理系統API服務運行中",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
