# Deploy JobMatch Platform to https://jobmatch.zip
# This script deploys both frontend and backend to Google Cloud Run with custom domain

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$Domain = "jobmatch.zip",
    [switch]$FrontendOnly = $false,
    [switch]$BackendOnly = $false
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Info($message) { Write-Host $message -ForegroundColor Cyan }
function Write-Success($message) { Write-Host $message -ForegroundColor Green }
function Write-Warning($message) { Write-Host $message -ForegroundColor Yellow }
function Write-Error($message) { Write-Host $message -ForegroundColor Red }

# Get project ID
if ([string]::IsNullOrEmpty($ProjectId)) {
    $ProjectId = gcloud config get-value project 2>$null
    if (-not $ProjectId) {
        Write-Error "❌ No GCP project configured. Set ProjectId parameter or run: gcloud config set project PROJECT_ID"
        exit 1
    }
}

Write-Info "🚀 Deploying JobMatch Platform to https://$Domain"
Write-Info "Project: $ProjectId"
Write-Info "Region: $Region"
Write-Host ""

# Check prerequisites
Write-Info "📋 Checking prerequisites..."
try {
    gcloud --version | Out-Null
    Write-Success "✅ gcloud CLI found"
} catch {
    Write-Error "❌ gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

try {
    docker --version | Out-Null
    Write-Success "✅ Docker found"
} catch {
    Write-Error "❌ Docker not found. Install from: https://www.docker.com/get-started"
    exit 1
}

# Authenticate
Write-Info "🔐 Authenticating Docker..."
gcloud auth configure-docker --quiet

# Enable required APIs
Write-Info "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com --project=$ProjectId --quiet
gcloud services enable run.googleapis.com --project=$ProjectId --quiet
gcloud services enable containerregistry.googleapis.com --project=$ProjectId --quiet
gcloud services enable servicenetworking.googleapis.com --project=$ProjectId --quiet

# Deploy Backend
if (-not $FrontendOnly) {
    Write-Info "`n📦 Deploying Backend..."
    
    $BackendServiceName = "jobmatch-backend"
    $BackendImage = "gcr.io/$ProjectId/$BackendServiceName`:latest"
    
    # Build backend image
    Write-Info "🔨 Building backend Docker image..."
    docker build -t $BackendImage -f Dockerfile.cloudrun .
    
    # Push image
    Write-Info "📤 Pushing backend image..."
    docker push $BackendImage
    
    # Deploy to Cloud Run
    Write-Info "🚀 Deploying backend to Cloud Run..."
    gcloud run deploy $BackendServiceName `
        --image $BackendImage `
        --platform managed `
        --region $Region `
        --project $ProjectId `
        --port 8080 `
        --memory 1Gi `
        --cpu 2 `
        --min-instances 1 `
        --max-instances 10 `
        --timeout 300 `
        --allow-unauthenticated `
        --set-env-vars "FRONTEND_URL=https://$Domain" `
        --quiet
    
    $BackendUrl = gcloud run services describe $BackendServiceName --region $Region --project $ProjectId --format="value(status.url)"
    Write-Success "✅ Backend deployed: $BackendUrl"
}

# Build Frontend
if (-not $BackendOnly) {
    Write-Info "`n📦 Building Frontend..."
    
    Push-Location frontend
    
    # Install dependencies
    Write-Info "📥 Installing frontend dependencies..."
    npm install
    
    # Build frontend
    Write-Info "🔨 Building frontend..."
    $env:NODE_ENV = "production"
    $env:VITE_API_URL = "https://api.$Domain"
    npm run build
    
    Pop-Location
    
    Write-Success "✅ Frontend built successfully"
}

# Create Frontend Dockerfile if it doesn't exist
if (-not (Test-Path "Dockerfile.frontend")) {
    Write-Info "📝 Creating frontend Dockerfile..."
    @"
# Frontend Dockerfile for Cloud Run
FROM nginx:alpine

# Copy built frontend
COPY frontend/dist /usr/share/nginx/html

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"@ | Out-File -FilePath "Dockerfile.frontend" -Encoding utf8
}

# Create nginx config if it doesn't exist
if (-not (Test-Path "frontend/nginx.conf")) {
    Write-Info "📝 Creating nginx configuration..."
    $nginxConfig = @"
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;

    # SPA routing - serve index.html for all routes
    location / {
        try_files `$uri `$uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass https://api.$Domain;
        proxy_http_version 1.1;
        proxy_set_header Upgrade `$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host `$host;
        proxy_cache_bypass `$http_upgrade;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"@
    New-Item -ItemType Directory -Force -Path "frontend" | Out-Null
    $nginxConfig | Out-File -FilePath "frontend/nginx.conf" -Encoding utf8
}

# Deploy Frontend
if (-not $BackendOnly) {
    Write-Info "`n📦 Deploying Frontend..."
    
    $FrontendServiceName = "jobmatch-frontend"
    $FrontendImage = "gcr.io/$ProjectId/$FrontendServiceName`:latest"
    
    # Build frontend image
    Write-Info "🔨 Building frontend Docker image..."
    docker build -t $FrontendImage -f Dockerfile.frontend .
    
    # Push image
    Write-Info "📤 Pushing frontend image..."
    docker push $FrontendImage
    
    # Deploy to Cloud Run
    Write-Info "🚀 Deploying frontend to Cloud Run..."
    gcloud run deploy $FrontendServiceName `
        --image $FrontendImage `
        --platform managed `
        --region $Region `
        --project $ProjectId `
        --port 8080 `
        --memory 512Mi `
        --cpu 1 `
        --min-instances 1 `
        --max-instances 5 `
        --timeout 60 `
        --allow-unauthenticated `
        --quiet
    
    $FrontendUrl = gcloud run services describe $FrontendServiceName --region $Region --project $ProjectId --format="value(status.url)"
    Write-Success "✅ Frontend deployed: $FrontendUrl"
}

# Map Custom Domain
Write-Info "`n🌐 Mapping custom domain..."
Write-Warning "⚠️  You need to verify domain ownership first:"
Write-Info "   1. Run: gcloud domains verify $Domain"
Write-Info "   2. Follow DNS verification instructions"
Write-Info "   3. Then run domain mapping commands below"
Write-Host ""

if (-not $BackendOnly) {
    Write-Info "Mapping frontend domain..."
    Write-Info "Run this command after domain verification:"
    Write-Host "gcloud run domain-mappings create --service=$FrontendServiceName --domain=$Domain --region=$Region --project=$ProjectId" -ForegroundColor Yellow
    Write-Host ""
}

Write-Info "Mapping API subdomain..."
Write-Info "Run this command after domain verification:"
Write-Host "gcloud run domain-mappings create --service=$BackendServiceName --domain=api.$Domain --region=$Region --project=$ProjectId" -ForegroundColor Yellow
Write-Host ""

# Summary
Write-Success "`n✅ Deployment Complete!"
Write-Info "`n📋 Next Steps:"
Write-Info "   1. Verify domain ownership: gcloud domains verify $Domain"
Write-Info "   2. Map frontend domain: gcloud run domain-mappings create --service=$FrontendServiceName --domain=$Domain --region=$Region"
Write-Info "   3. Map API domain: gcloud run domain-mappings create --service=$BackendServiceName --domain=api.$Domain --region=$Region"
Write-Info "   4. Update DNS records as instructed by domain mapping commands"
Write-Info "   5. Wait for SSL certificate provisioning (can take up to 15 minutes)"
Write-Host ""
Write-Success "🎉 Your app will be available at:"
if (-not $BackendOnly) {
    Write-Host "   Frontend: https://$Domain" -ForegroundColor Green
}
if (-not $FrontendOnly) {
    Write-Host "   Backend API: https://api.$Domain" -ForegroundColor Green
}

