"""
SEO API Endpoints
Google Search Console integration and SEO management
"""
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from database.connection import get_db
from seo.search_console import SearchConsoleManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/seo", tags=["seo"])


class SitemapSubmitRequest(BaseModel):
    """Request to submit sitemap."""
    sitemap_url: Optional[str] = None


class IndexRequest(BaseModel):
    """Request to index a URL."""
    url: str


class SearchAnalyticsRequest(BaseModel):
    """Request for search analytics."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    dimensions: Optional[List[str]] = None
    row_limit: int = 1000


class KeywordOptimizationRequest(BaseModel):
    """Request for keyword optimization."""
    keywords: Optional[List[str]] = None


@router.post("/sitemap/submit")
async def submit_sitemap(
    request: SitemapSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit sitemap to Google Search Console.
    
    Args:
        request: Sitemap submission request
    
    Returns:
        Submission status
    """
    manager = SearchConsoleManager()
    result = manager.submit_sitemap(request.sitemap_url)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/index/request")
async def request_indexing(
    request: IndexRequest,
    db: Session = Depends(get_db)
):
    """
    Request indexing for a specific URL.
    
    Args:
        request: Index request with URL
    
    Returns:
        Indexing request status
    """
    manager = SearchConsoleManager()
    result = manager.request_indexing(request.url)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/sitemaps")
async def get_sitemaps(db: Session = Depends(get_db)):
    """Get list of submitted sitemaps."""
    manager = SearchConsoleManager()
    return manager.get_sitemaps()


@router.get("/index/status")
async def get_index_status(db: Session = Depends(get_db)):
    """Get overall indexing status."""
    manager = SearchConsoleManager()
    return manager.get_index_status()


@router.post("/analytics/search")
async def get_search_analytics(
    request: SearchAnalyticsRequest,
    db: Session = Depends(get_db)
):
    """
    Get search analytics data.
    
    Args:
        request: Analytics request with date range and dimensions
    
    Returns:
        Search analytics data
    """
    manager = SearchConsoleManager()
    result = manager.get_search_analytics(
        start_date=request.start_date,
        end_date=request.end_date,
        dimensions=request.dimensions,
        row_limit=request.row_limit
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/analytics/search")
async def get_search_analytics_get(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    dimensions: Optional[str] = Query(None, description="Comma-separated dimensions"),
    row_limit: int = Query(1000, description="Maximum rows"),
    db: Session = Depends(get_db)
):
    """
    Get search analytics data (GET version).
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        dimensions: Comma-separated dimensions
        row_limit: Maximum rows to return
    
    Returns:
        Search analytics data
    """
    manager = SearchConsoleManager()
    
    dim_list = None
    if dimensions:
        dim_list = [d.strip() for d in dimensions.split(",")]
    
    result = manager.get_search_analytics(
        start_date=start_date,
        end_date=end_date,
        dimensions=dim_list,
        row_limit=row_limit
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/keywords/optimize")
async def optimize_keywords(
    request: KeywordOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze and optimize for target keywords.
    
    Args:
        request: Keyword optimization request
    
    Returns:
        Optimization recommendations
    """
    manager = SearchConsoleManager()
    result = manager.optimize_keywords(request.keywords)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/keywords/optimize")
async def optimize_keywords_get(
    keywords: Optional[str] = Query(None, description="Comma-separated keywords"),
    db: Session = Depends(get_db)
):
    """
    Analyze and optimize for target keywords (GET version).
    
    Args:
        keywords: Comma-separated list of keywords
    
    Returns:
        Optimization recommendations
    """
    manager = SearchConsoleManager()
    
    keyword_list = None
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",")]
    
    result = manager.optimize_keywords(keyword_list)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/status")
async def get_seo_status(db: Session = Depends(get_db)):
    """Get overall SEO status and health."""
    manager = SearchConsoleManager()
    
    status = {
        "api_initialized": manager.service is not None,
        "site_url": manager.site_url,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if manager.service:
        # Get sitemaps
        sitemaps_result = manager.get_sitemaps()
        if sitemaps_result.get("status") == "success":
            status["sitemaps"] = sitemaps_result.get("sitemaps", [])
        
        # Get index status
        index_result = manager.get_index_status()
        if index_result.get("status") == "success":
            status["index_status"] = index_result
    else:
        status["error"] = "Search Console API not initialized. Check credentials."
    
    return status

