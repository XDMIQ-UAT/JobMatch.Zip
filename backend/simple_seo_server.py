"""
Simple standalone SEO server - no database dependencies
Run: python simple_seo_server.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.seo.search_console import SearchConsoleManager

app = FastAPI(title="SEO Server", description="Google Search Console API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SEO Server", "endpoints": ["/api/seo/status", "/health"]}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/seo/status")
async def seo_status():
    manager = SearchConsoleManager()
    status = {
        "api_initialized": manager.service is not None,
        "site_url": manager.site_url,
    }
    if manager.service:
        try:
            sitemaps = manager.get_sitemaps()
            status["sitemaps"] = sitemaps.get("sitemaps", [])
        except:
            pass
    return status

if __name__ == "__main__":
    import uvicorn
    print("Starting SEO Server on http://localhost:8000")
    print("Test: curl http://localhost:8000/api/seo/status")
    uvicorn.run(app, host="0.0.0.0", port=8000)

