"""
Main FastAPI application for paperwork generation.

Provides HTTP endpoints for generating loadsheets and timesheets from JSON data.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .schemas import (
    LoadsheetRequest,
    TimesheetRequest,
    GenerateResponse,
    HealthResponse,
    SignatureListResponse,
)
from .services.loadsheet import generate_loadsheet
from .services.timesheet import generate_timesheet

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("paperworkgen")

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint returning basic API information."""
    return {
        "message": "Paperwork Generation API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.api_version
    )


@app.post("/api/loadsheet/generate", response_model=GenerateResponse, summary="Generate loadsheet")
async def create_loadsheet(request: LoadsheetRequest):
    """
    Generate a loadsheet Excel and PDF from JSON data.
    
    The loadsheet will be saved to the appropriate week folder based on the load date.
    """
    try:
        logger.info(f"Generating loadsheet for load {request.load_number}")
        result = generate_loadsheet(request)
        logger.info(f"Loadsheet generated successfully: {result.excel_path}")
        return result
    except FileNotFoundError as e:
        logger.error(f"Template not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid request data: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating loadsheet: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during loadsheet generation")


@app.post("/api/timesheet/generate", response_model=GenerateResponse, summary="Generate timesheet")
async def create_timesheet(request: TimesheetRequest):
    """
    Generate a weekly timesheet Excel and PDF from JSON data.
    
    The timesheet will be saved to the appropriate week folder based on the week ending date.
    """
    try:
        logger.info(f"Generating timesheet for driver {request.driver}, week ending {request.week_ending}")
        result = generate_timesheet(request)
        logger.info(f"Timesheet generated successfully: {result.excel_path}")
        return result
    except FileNotFoundError as e:
        logger.error(f"Template not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid request data: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating timesheet: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during timesheet generation")


@app.get("/api/signatures", response_model=SignatureListResponse, summary="List available signatures")
async def list_signatures():
    """
    List available signature images.
    
    Returns lists of available signature images in sig1 and sig2 directories.
    """
    try:
        sig1_images = []
        sig2_images = []
        
        # Get sig1 images
        if settings.sig1_dir.exists():
            sig1_images = [
                f.name for f in settings.sig1_dir.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
            ]
        
        # Get sig2 images
        if settings.sig2_dir.exists():
            sig2_images = [
                f.name for f in settings.sig2_dir.iterdir()
                if f.suffix.lower() in {".png", ".jpg", ".jpeg"}
            ]
        
        return SignatureListResponse(
            sig1_images=sorted(sig1_images),
            sig2_images=sorted(sig2_images)
        )
    except Exception as e:
        logger.error(f"Error listing signatures: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving signature list")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
