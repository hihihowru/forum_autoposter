from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

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

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Forum Auto Poster API is running",
        "endpoints": [
            "/api/health"
        ]
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# This is needed for Vercel to work properly
handler = Mangum(app)
