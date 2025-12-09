"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from pptx_accessibility.core.config import settings
from pptx_accessibility.core.session_manager import SessionManager

# Global session manager instance
session_manager: SessionManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global session_manager

    # Startup
    logger.info("Starting PowerPoint & PDF Accessibility Checker")
    logger.info(f"Storage root: {settings.storage_root}")

    # Initialize session manager
    session_manager = SessionManager(settings.storage_root)

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title="PowerPoint & PDF Accessibility Checker",
    description="Automatic accessibility adaptation of PowerPoint and PDF documents",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check (moved before static files mounting)
@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and mount routes
from pptx_accessibility.api.routes import upload, analysis

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

# Mount static files (web frontend)
# Serve the web interface from web/public directory
import os
from pathlib import Path

# Get the project root directory (3 levels up from this file)
project_root = Path(__file__).parent.parent.parent.parent
web_public_dir = project_root / "web" / "public"

if web_public_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_public_dir), html=True), name="static")
    logger.info(f"Serving static files from: {web_public_dir}")
else:
    logger.warning(f"Web public directory not found: {web_public_dir}")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )
