# Deploy Agents to Cloud Run
# This script builds and deploys the agent service to Cloud Run

param(
    [string]$ProjectId = "futurelink-private-112912460",
    [string]$Region = "us-central1",
    [string]$ServiceName = "agent-service",
    [switch]$BuildOnly = $false,
    [switch]$DeployOnly = $false
)

$ErrorActionPreference = "Continue"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Deploy Agents to Cloud Run" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectId" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "Service: $ServiceName" -ForegroundColor Yellow
Write-Host ""

# Set project
Write-Host "Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Project set: $ProjectId" -ForegroundColor Green
Write-Host ""

# Enable required APIs
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "secretmanager.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "  Checking $api..." -ForegroundColor Gray
    gcloud services enable $api --quiet 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $api enabled" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $api (may already be enabled)" -ForegroundColor Yellow
    }
}
Write-Host ""

# Build and push image
if (-not $DeployOnly) {
    Write-Host "Building and pushing container image..." -ForegroundColor Yellow
    
    $imageTag = "gcr.io/$ProjectId/$ServiceName"
    
    # Use Cloud Build (recommended)
    Write-Host "  Using Cloud Build..." -ForegroundColor Gray
    
    # Build from project root to include workflow files
    $originalLocation = Get-Location
    Push-Location (Get-Location).Parent
    
    # Get commit SHA for versioning
    $commitSha = git rev-parse --short HEAD 2>$null
    if (-not $commitSha) {
        $commitSha = "latest"
    }
    
    # Use Cloud Build with substitutions
    Write-Host "  Building with Dockerfile.prod (commit: $commitSha)..." -ForegroundColor Gray
    
    # Build directly with gcloud builds submit
    gcloud builds submit `
        --config agents-cloud-run/cloudbuild.yaml `
        --substitutions _SHORT_SHA=$commitSha `
        .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Pop-Location
    Write-Host "✅ Image built and pushed" -ForegroundColor Green
    Write-Host ""
}

if ($BuildOnly) {
    Write-Host "Build only - skipping deployment" -ForegroundColor Yellow
    exit 0
}

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow

# Use the latest image tag
$imageTag = "gcr.io/$ProjectId/$ServiceName:latest"

# Get environment variables from .env.local if exists
$envVars = @()
if (Test-Path ".env.local") {
    $envContent = Get-Content ".env.local" -Raw
    if ($envContent -match "NEXT_PUBLIC_GTM_ID=(.+)") {
        $gtmId = $matches[1].Trim()
        $envVars += "NEXT_PUBLIC_GTM_ID=$gtmId"
    }
}

# Build deploy command using splatting
$deployArgs = @(
    "run", "deploy", $ServiceName,
    "--image", $imageTag,
    "--platform", "managed",
    "--region", $Region,
    "--allow-unauthenticated",
    "--memory", "512Mi",
    "--cpu", "1",
    "--min-instances", "0",
    "--max-instances", "10",
    "--timeout", "300",
    "--port", "8080"
)

if ($envVars.Count -gt 0) {
    $envVarsStr = $envVars -join ","
    $deployArgs += "--set-env-vars", $envVarsStr
}

Write-Host "  Deploying..." -ForegroundColor Gray
Write-Host "  Image: $imageTag" -ForegroundColor Gray
gcloud @deployArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host ""

# Get service URL
Write-Host "Getting service URL..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $ServiceName --region $Region --format="value(status.url)" 2>&1
if ($LASTEXITCODE -eq 0 -and $serviceUrl) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Deployment Complete!" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "Test endpoints:" -ForegroundColor Yellow
    Write-Host "  Health: $serviceUrl/health" -ForegroundColor White
    Write-Host "  Workflows: $serviceUrl/workflows" -ForegroundColor White
    Write-Host "  Execute: $serviceUrl/workflows/execute" -ForegroundColor White
    Write-Host ""
    Write-Host "View logs:" -ForegroundColor Yellow
    Write-Host "  gcloud logging tail `"resource.type=cloud_run_revision AND resource.labels.service_name=$ServiceName`"" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  Could not retrieve service URL" -ForegroundColor Yellow
    Write-Host "   Check Cloud Run console: https://console.cloud.google.com/run" -ForegroundColor White
}

Write-Host "================================================" -ForegroundColor Cyan

