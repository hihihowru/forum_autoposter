from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import Optional
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="Forum Auto Poster API",
    description="API for the Forum Auto Poster application",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Forum Auto Poster API is running"
    }

# Import your main application components here
# from src.core.main_workflow_engine import MainWorkflowEngine

# Example endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# This is needed for Vercel to work properly
app = app
