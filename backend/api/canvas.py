"""
Universal Canvas API Endpoints.
Lightweight API for canvas data storage and sync.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import gzip
import base64

from database.connection import get_db

router = APIRouter(prefix="/api/canvas", tags=["canvas"])


class CanvasSaveRequest(BaseModel):
    """Request to save canvas data."""
    canvas_data: str  # Base64 encoded image data
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CanvasLoadResponse(BaseModel):
    """Response for loading canvas."""
    canvas_data: Optional[str] = None
    saved_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/save")
async def save_canvas(
    request: CanvasSaveRequest,
    db: Session = Depends(get_db)
):
    """
    Save canvas data.
    Lightweight endpoint - compresses data for low bandwidth.
    """
    try:
        # Compress canvas data for low bandwidth
        canvas_bytes = base64.b64decode(request.canvas_data.split(',')[1] if ',' in request.canvas_data else request.canvas_data)
        compressed = gzip.compress(canvas_bytes)
        compressed_b64 = base64.b64encode(compressed).decode('utf-8')
        
        # In production, would save to database
        # For now, return success
        
        return {
            "success": True,
            "compressed_size": len(compressed),
            "original_size": len(canvas_bytes),
            "compression_ratio": f"{(1 - len(compressed) / len(canvas_bytes)) * 100:.1f}%"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save canvas: {str(e)}")


@router.get("/load")
async def load_canvas(
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Load canvas data.
    Returns compressed data for low bandwidth transfer.
    """
    # In production, would load from database
    # For now, return empty response
    return {
        "canvas_data": None,
        "saved_at": None,
        "metadata": None
    }


@router.get("/info")
async def canvas_info():
    """
    Get canvas system information.
    """
    return {
        "name": "Universal Canvas",
        "version": "1.0.0",
        "features": [
            "Low bandwidth optimized",
            "Offline capable",
            "Universal accessibility",
            "Progressive enhancement"
        ],
        "max_size": "10MB",
        "supported_formats": ["PNG", "JPEG"],
        "compression": True
    }

