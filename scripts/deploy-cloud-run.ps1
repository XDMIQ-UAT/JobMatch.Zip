# Deploy to Google Cloud Run - PowerShell Script
# Usage: .\scripts\deploy-cloud-run.ps1 [-ServiceName "service-name"] [-Region "region"] [-ImageTag "tag"]

param(
    [string]$ServiceName = $env:SERVICE_NAME,
    [string]$Region = $env:GCP_REGION,
    [string]$ImageTag = "latest",
    [string]$ProjectId = $env:GCP_PROJECT_ID
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Get project ID if not set
if (-not $ProjectId) {
    try {
        $ProjectId = (gcloud config get-value project 2>$null)
    } catch {
        Write-ColorOutput Red "Error: PROJECT_ID not set. Set GCP_PROJECT_ID or run 'gcloud config set project PROJECT_ID'"
        exit 1
    }
}

# Set defaults
if (-not $ServiceName) {
    $ServiceName = "jobmatch-backend"
}
if (-not $Region) {
    $Region = "us-central1"
}

$ImageName = "gcr.io/${ProjectId}/${ServiceName}:${ImageTag}"

Write-ColorOutput Green "🚀 Deploying to Google Cloud Run"
Write-Output "Project ID: $ProjectId"
Write-Output "Service Name: $ServiceName"
Write-Output "Region: $Region"
Write-Output "Image: $ImageName"
Write-Output ""

# Check if gcloud is installed
try {
    gcloud --version | Out-Null
} catch {
    Write-ColorOutput Red "Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
}

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-ColorOutput Red "Error: Docker not found. Please install Docker."
    exit 1
}

# Authenticate
Write-ColorOutput Yellow "📋 Authenticating..."
gcloud auth configure-docker --quiet

# Build image
Write-ColorOutput Yellow "🔨 Building Docker image..."
docker build -t $ImageName -f Dockerfile .

# Push image
Write-ColorOutput Yellow "📤 Pushing image to GCR..."
docker push $ImageName

# Deploy to Cloud Run
Write-ColorOutput Yellow "🚀 Deploying to Cloud Run..."
gcloud run deploy $ServiceName `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --port 8080 `
    --memory 512Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10 `
    --timeout 300 `
    --allow-unauthenticated `
    --quiet

# Get service URL
$ServiceUrl = gcloud run services describe $ServiceName `
    --region $Region `
    --format="value(status.url)"

Write-Output ""
Write-ColorOutput Green "✅ Deployment successful!"
Write-ColorOutput Green "Service URL: $ServiceUrl"
Write-Output ""
Write-Output "View logs: gcloud logging tail `"resource.type=cloud_run_revision AND resource.labels.service_name=$ServiceName`""
Write-Output "Update service: gcloud run services update $ServiceName --region $Region"

