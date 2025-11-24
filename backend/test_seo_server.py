"""
Minimal test server for SEO endpoints only
Bypasses database dependencies to test SEO API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from seo.search_console import SearchConsoleManager
from api.seo import router as seo_router

app = FastAPI(title="SEO Test Server", description="Test Google Search Console API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include SEO router
app.include_router(seo_router)

@app.get("/")
async def root():
    return {"message": "SEO Test Server", "endpoints": ["/api/seo/status", "/api/seo/sitemaps"]}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "seo-test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

