"""
VCOS Gateway - Main HTTP/gRPC server
Receives requests to create content batch, triggers hook generation, triggers pipeline
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gateway.routing import router
from gateway.auth import validate_api_key
from gateway.rate_limits import RateLimiter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VCOS Gateway",
    description="Viral Content Operating System - Distribution Intelligence Gateway",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
rate_limiter = RateLimiter()

# Include routers
app.include_router(router)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vcos-gateway"}

@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    logger.info("VCOS Gateway starting up...")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("VCOS Gateway shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
