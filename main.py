"""
最簡單的測試 API - 直接在根目錄
"""

from fastapi import FastAPI
import os
from datetime import datetime

app = FastAPI(title="Test API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "Test API is running",
        "status": "healthy",
        "port": os.getenv("PORT", "unknown"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "API is working",
        "port": os.getenv("PORT", "unknown"),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)