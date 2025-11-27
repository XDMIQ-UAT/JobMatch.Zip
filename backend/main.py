"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
# Temporarily slim imports to avoid cascading import failures
from api import voice, subscription, age_verification, zero_knowledge_auth, zero_knowledge_matching, google_oauth, social_auth
from security.security_headers import SecurityHeadersMiddleware
from security.rate_limiter import RateLimiterMiddleware

# Read version
try:
    with open("VERSION", "r") as f:
        app_version = f.read().strip().split("\n")[0]
except:
    app_version = "REV001"

app = FastAPI(
    title="AI-Enabled LLC Matching Platform",
    description="Job matching platform for LLC owners who work with AI",
    version=app_version,
)

# Security middleware (applied first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware, requests_per_minute=60)

# CORS middleware (restrict in production)
# Specify explicit methods and headers for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Accept-Language",
        "X-Requested-With",
        "X-CSRF-Token",
        "Cache-Control",
    ],
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include routers
# Minimal routers to bring up critical endpoints
app.include_router(voice.router)  # Twilio voice integration
app.include_router(subscription.router)  # Stripe subscription management
app.include_router(age_verification.router)  # COPPA compliance
app.include_router(zero_knowledge_auth.router)  # Zero-knowledge authentication
app.include_router(zero_knowledge_matching.router)  # Zero-knowledge matching
app.include_router(google_oauth.router)  # Google OAuth
app.include_router(social_auth.router)  # Social authentication (email, SMS, etc.)
# GCP CLI Backdoor (Documented Feature) - Disabled for now
# if settings.GCP_CLI_ENABLED:
#     from api import gcp_cli
#     app.include_router(gcp_cli.router)


@app.get("/")
async def root():
    """Root endpoint."""
    try:
        with open("VERSION", "r") as f:
            version = f.read().strip().split("\n")[0]
    except:
        version = "REV001"
    
    return JSONResponse({
        "message": "AI-Enabled LLC Matching Platform API",
        "version": version,
        "release": "REV001",
        "status": "operational"
    })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        with open("VERSION", "r") as f:
            version = f.read().strip().split("\n")[0]
    except:
        version = "REV001"
    
    return JSONResponse({
        "status": "healthy",
        "service": "backend",
        "version": version,
        "release": "REV001"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

