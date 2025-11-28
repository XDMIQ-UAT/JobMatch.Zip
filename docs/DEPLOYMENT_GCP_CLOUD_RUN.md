# Deploying to Google Cloud Run - Complete Guide

This guide provides step-by-step instructions for deploying a web application to Google Cloud Run, including Docker setup, container registry, deployment, and best practices.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Dockerfile Creation](#dockerfile-creation)
4. [Building and Pushing to GCR](#building-and-pushing-to-gcr)
5. [Deploying via Console](#deploying-via-console)
6. [Deploying via CLI](#deploying-via-cli)
7. [Environment Variables](#environment-variables)
8. [Security Best Practices](#security-best-practices)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

1. **Google Cloud SDK (gcloud)**
   ```bash
   # Install gcloud CLI
   # macOS
   brew install google-cloud-sdk
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   
   # Windows
   # Download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Docker**
   ```bash
   # Verify Docker is installed
   docker --version
   docker-compose --version
   ```

3. **Google Cloud Account**
   - Active Google Cloud account
   - Billing enabled on your project

### Initial Setup

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Verify setup
gcloud config list
```

---

## Project Setup

### 1. Create Google Cloud Project (if needed)

```bash
# Create new project
gcloud projects create YOUR_PROJECT_ID --name="Your Project Name"

# Set as active project
gcloud config set project YOUR_PROJECT_ID

# Link billing account (required)
gcloud billing projects link YOUR_PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

### 2. Configure Application ID

Set your project ID as an environment variable for convenience:

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"  # or your preferred region
export SERVICE_NAME="your-service-name"
```

---

## Dockerfile Creation

### Best Practices for Cloud Run Dockerfiles

Cloud Run has specific requirements:
- Container must listen on `PORT` environment variable (default: 8080)
- Should handle graceful shutdown
- Optimize for fast cold starts

### Example Dockerfile (Python/FastAPI)

```dockerfile
# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Cloud Run sets PORT env var)
EXPOSE 8080

# Use environment variable for port
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')" || exit 1

# Run application
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 --access-logfile - --error-logfile - app:app
```

### Example Dockerfile (Node.js/Express)

```dockerfile
# Use Node.js slim image
FROM node:20-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Use PORT environment variable
ENV PORT=8080
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:${PORT}/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["node", "server.js"]
```

### Example Dockerfile (Python/JobMatch Backend)

```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY backend/ ./backend/
COPY shared/ ./shared/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Cloud Run port
ENV PORT=8080
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')" || exit 1

# Run with gunicorn
CMD exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    backend.main:app
```

### .dockerignore File

Create a `.dockerignore` file to exclude unnecessary files:

```
# Git
.git
.gitignore
.gitattributes

# Documentation
*.md
docs/
README.md

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Dependencies (if copying node_modules)
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Build outputs
dist/
build/
*.egg-info/

# Logs
logs/
*.log

# Tests
tests/
test_*.py
*.test.js

# CI/CD
.github/
.gitlab-ci.yml
```

---

## Building and Pushing to GCR

### Method 1: Using Cloud Build (Recommended)

Cloud Build is the recommended way to build and push images:

```bash
# Submit build to Cloud Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Or with specific Dockerfile location
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --file Dockerfile.prod .
```

### Method 2: Local Build and Push

```bash
# Authenticate Docker with GCR
gcloud auth configure-docker

# Build image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# Tag for specific version
docker tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    gcr.io/$PROJECT_ID/$SERVICE_NAME:v1.0.0

# Push to GCR
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:v1.0.0
```

### Method 3: Using Cloud Build Configuration File

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/$SERVICE_NAME:$SHORT_SHA', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/$SERVICE_NAME:$SHORT_SHA']
  
  # Tag as latest
  - name: 'gcr.io/cloud-builders/docker'
    args: ['tag', 'gcr.io/$PROJECT_ID/$SERVICE_NAME:$SHORT_SHA', 'gcr.io/$PROJECT_ID/$SERVICE_NAME:latest']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/$SERVICE_NAME:latest']

images:
  - 'gcr.io/$PROJECT_ID/$SERVICE_NAME:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/$SERVICE_NAME:latest'

options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
```

Then build:

```bash
gcloud builds submit --config cloudbuild.yaml
```

---

## Deploying via Console

### Step 1: Access Cloud Run Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Run** → **Create Service**

### Step 2: Configure Service

1. **Service Name**: Enter your service name
2. **Region**: Select your preferred region
3. **Deploy one revision from an existing container image**: Select this option
4. **Container Image URL**: `gcr.io/YOUR_PROJECT_ID/YOUR_SERVICE_NAME:latest`

### Step 3: Configure Container

1. **Container Port**: `8080` (or your PORT env var)
2. **CPU Allocation**: 
   - **CPU is only allocated during request processing** (recommended for cost savings)
   - Or **CPU is always allocated** (for consistent performance)
3. **Memory**: Select appropriate amount (start with 512Mi, adjust based on needs)
4. **Maximum number of instances**: Set limit (e.g., 10)
5. **Minimum number of instances**: `0` (for cost savings) or `1` (for faster cold starts)

### Step 4: Set Environment Variables

Click **Variables & Secrets** tab:
- Add environment variables (see [Environment Variables](#environment-variables) section)
- Reference secrets from Secret Manager (recommended)

### Step 5: Configure Security

1. **Authentication**: 
   - **Allow unauthenticated invocations** (for public APIs)
   - Or **Require authentication** (for private APIs)

2. **Service Account**: Select or create service account with minimal permissions

### Step 6: Advanced Settings

1. **Networking**: 
   - VPC connector (if needed)
   - Ingress: **All** or **Internal**
2. **Connections**: 
   - Timeout: `300` seconds (max)
   - Request timeout: `300` seconds
3. **Container**: 
   - Startup probe (if needed)
   - Liveness probe (if needed)

### Step 7: Deploy

Click **Create** and wait for deployment to complete.

---

## Deploying via CLI

### Basic Deployment

```bash
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated
```

### Advanced Deployment with Options

```bash
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80 \
    --allow-unauthenticated \
    --service-account SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars "ENV=production,LOG_LEVEL=info" \
    --set-secrets "DATABASE_URL=database-url:latest,API_KEY=api-key:latest" \
    --vpc-connector projects/PROJECT_ID/locations/REGION/connectors/CONNECTOR_NAME \
    --vpc-egress all-traffic
```

### Deploy with YAML Configuration

Create `service.yaml`:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: your-service-name
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "true"
        run.googleapis.com/execution-environment: gen2
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      serviceAccountName: SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com
      containers:
      - image: gcr.io/PROJECT_ID/SERVICE_NAME:latest
        ports:
        - name: http1
          containerPort: 8080
        env:
        - name: PORT
          value: "8080"
        - name: ENV
          value: "production"
        resources:
          limits:
            cpu: "1"
            memory: 512Mi
        startupProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 0
          timeoutSeconds: 240
          periodSeconds: 240
          failureThreshold: 1
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 0
          timeoutSeconds: 1
          periodSeconds: 3
```

Deploy:

```bash
gcloud run services replace service.yaml --region $REGION
```

### Update Existing Service

```bash
# Update image
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:v1.0.1 \
    --region $REGION

# Update environment variables
gcloud run services update $SERVICE_NAME \
    --update-env-vars "NEW_VAR=value" \
    --region $REGION

# Update memory
gcloud run services update $SERVICE_NAME \
    --memory 1Gi \
    --region $REGION
```

---

## Environment Variables

### Setting Environment Variables

#### Via Console
1. Go to Cloud Run service
2. Click **Edit & Deploy New Revision**
3. Go to **Variables & Secrets** tab
4. Add variables under **Environment Variables**

#### Via CLI

```bash
# Set single variable
gcloud run services update $SERVICE_NAME \
    --update-env-vars "KEY=value" \
    --region $REGION

# Set multiple variables
gcloud run services update $SERVICE_NAME \
    --update-env-vars "KEY1=value1,KEY2=value2,KEY3=value3" \
    --region $REGION

# Remove variable
gcloud run services update $SERVICE_NAME \
    --remove-env-vars "KEY" \
    --region $REGION
```

### Using Secret Manager (Recommended)

#### 1. Create Secret

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create SECRET_NAME \
    --data-file=- \
    --replication-policy="automatic"

# Or from file
gcloud secrets create SECRET_NAME \
    --data-file=path/to/secret.txt \
    --replication-policy="automatic"
```

#### 2. Grant Access

```bash
# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding SECRET_NAME \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### 3. Reference in Deployment

```bash
gcloud run deploy $SERVICE_NAME \
    --set-secrets "ENV_VAR_NAME=SECRET_NAME:latest" \
    --region $REGION
```

#### 4. Access in Code

```python
# Python example
import os
from google.cloud import secretmanager

def get_secret(secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.getenv('PROJECT_ID')}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Use in application
DATABASE_URL = get_secret("database-url")
```

### Environment Variable Best Practices

1. **Never commit secrets** to version control
2. **Use Secret Manager** for sensitive data
3. **Use environment-specific values** (dev, staging, prod)
4. **Document all variables** in README or docs
5. **Validate required variables** at startup

Example validation:

```python
# Python example
import os

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "API_KEY",
    "REDIS_URL"
]

def validate_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")

# Call at startup
validate_env()
```

---

## Security Best Practices

### 1. Use Service Accounts

Create a service account with minimal permissions:

```bash
# Create service account
gcloud iam service-accounts create cloud-run-sa \
    --display-name="Cloud Run Service Account"

# Grant minimal permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-run-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Use in deployment
gcloud run deploy $SERVICE_NAME \
    --service-account cloud-run-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --region $REGION
```

### 2. Enable IAM Authentication

```bash
# Require authentication
gcloud run services update $SERVICE_NAME \
    --no-allow-unauthenticated \
    --region $REGION

# Grant access to specific users/service accounts
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --member="user:user@example.com" \
    --role="roles/run.invoker" \
    --region $REGION
```

### 3. Use VPC Connector for Private Resources

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create CONNECTOR_NAME \
    --region=$REGION \
    --subnet=SUBNET_NAME \
    --subnet-project=$PROJECT_ID \
    --min-instances=2 \
    --max-instances=3

# Use in deployment
gcloud run deploy $SERVICE_NAME \
    --vpc-connector CONNECTOR_NAME \
    --vpc-egress private-ranges-only \
    --region $REGION
```

### 4. Enable Binary Authorization

```bash
# Enable Binary Authorization
gcloud container binauthz policy import policy.yaml

# Create policy
cat > policy.yaml <<EOF
admissionWhitelistPatterns:
- namePattern: gcr.io/$PROJECT_ID/*
clusterAdmissionRules:
  us-central1-a.cluster:
    enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
    evaluationMode: REQUIRE_ATTESTATION
EOF
```

### 5. Scan Container Images

```bash
# Enable Container Analysis API
gcloud services enable containeranalysis.googleapis.com

# Scan image
gcloud container images scan gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
```

### 6. Use HTTPS Only

Cloud Run automatically provides HTTPS. Ensure your application:
- Redirects HTTP to HTTPS
- Uses secure cookies
- Implements HSTS headers

### 7. Implement Rate Limiting

```python
# Python example with Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/endpoint")
@limiter.limit("10 per minute")
def api_endpoint():
    return {"status": "ok"}
```

### 8. Security Headers

```python
# Python example
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## Monitoring and Logging

### 1. Cloud Logging

Cloud Run automatically sends logs to Cloud Logging. View logs:

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit 50 \
    --format json

# Follow logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME"
```

### 2. Structured Logging

Implement structured logging in your application:

```python
# Python example
import json
import logging
import sys

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, message, **kwargs):
        log_entry = {
            "severity": "INFO",
            "message": message,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))
    
    def error(self, message, **kwargs):
        log_entry = {
            "severity": "ERROR",
            "message": message,
            **kwargs
        }
        self.logger.error(json.dumps(log_entry))

# Usage
logger = StructuredLogger(__name__)
logger.info("Request processed", user_id=123, duration_ms=45)
```

### 3. Cloud Monitoring Metrics

Cloud Run automatically provides metrics:
- Request count
- Request latency
- Error rate
- Instance count
- CPU utilization
- Memory utilization

View metrics:

```bash
# Query metrics
gcloud monitoring time-series list \
    --filter='resource.type="cloud_run_revision" AND resource.labels.service_name="$SERVICE_NAME"'
```

### 4. Custom Metrics

```python
# Python example with OpenCensus
from opencensus.ext.stackdriver import stats_exporter
from opencensus.stats import stats as stats_module

# Create exporter
exporter = stats_exporter.new_stats_exporter()

# Create metric
stats = stats_module.stats
view_manager = stats.view_manager
stats_recorder = stats.stats_recorder

# Define custom metric
custom_metric = stats_module.MeasureInt("custom_metric", "A custom metric", "count")
view = stats_module.View(
    "custom_metric_view",
    "A custom metric view",
    [],
    custom_metric,
    stats_module.aggregation.CountAggregation()
)
view_manager.register_view(view)

# Record metric
mmap = stats_recorder.new_measurement_map()
mmap.measure_int_put(custom_metric, 1)
mmap.record()
```

### 5. Error Reporting

```python
# Python example
from google.cloud import error_reporting

error_client = error_reporting.Client()

try:
    # Your code
    pass
except Exception as e:
    error_client.report_exception()
    raise
```

### 6. Alerts

Create alerting policies:

```bash
# Create alert policy
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=0.05 \
    --condition-threshold-duration=300s \
    --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'
```

### 7. Health Checks

Implement health check endpoints:

```python
# Python example
@app.route("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.route("/ready")
def ready():
    # Check database connection, etc.
    try:
        db.ping()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}, 503
```

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit 100

# Check container image
gcloud container images describe gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
```

#### 2. Port Not Listening

Ensure your application listens on the PORT environment variable:

```python
# Python example
import os
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
```

#### 3. Cold Start Issues

- Increase minimum instances: `--min-instances 1`
- Optimize container image size
- Use Cloud CDN for static assets
- Implement health checks

#### 4. Memory Issues

```bash
# Increase memory
gcloud run services update $SERVICE_NAME \
    --memory 1Gi \
    --region $REGION
```

#### 5. Timeout Issues

```bash
# Increase timeout
gcloud run services update $SERVICE_NAME \
    --timeout 300 \
    --region $REGION
```

#### 6. Authentication Issues

```bash
# Check IAM policy
gcloud run services get-iam-policy $SERVICE_NAME --region $REGION

# Test with authenticated request
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    https://SERVICE_URL
```

### Debugging Commands

```bash
# List all revisions
gcloud run revisions list --service $SERVICE_NAME --region $REGION

# Describe service
gcloud run services describe $SERVICE_NAME --region $REGION

# Get service URL
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"

# View recent deployments
gcloud run revisions list --service $SERVICE_NAME --region $REGION --limit 5
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

env:
  PROJECT_ID: your-project-id
  SERVICE_NAME: your-service-name
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - id: 'auth'
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: 'Set up Cloud SDK'
        uses: 'google-github-actions/setup-gcloud@v1'
      
      - name: 'Configure Docker'
        run: gcloud auth configure-docker
      
      - name: 'Build and Push'
        run: |
          docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA .
          docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA
          docker tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
              gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
          docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
      
      - name: 'Deploy'
        run: |
          gcloud run deploy $SERVICE_NAME \
            --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated
```

### GitLab CI Example

```yaml
deploy:
  stage: deploy
  image: google/cloud-sdk:latest
  script:
    - gcloud auth activate-service-account --key-file=$GCP_SERVICE_ACCOUNT_KEY
    - gcloud config set project $PROJECT_ID
    - gcloud auth configure-docker
    - docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$CI_COMMIT_SHA .
    - docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$CI_COMMIT_SHA
    - gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$CI_COMMIT_SHA \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated
```

---

## Cost Optimization

### Tips to Reduce Costs

1. **Use CPU throttling**: Only allocate CPU during requests
2. **Set minimum instances to 0**: Scale to zero when not in use
3. **Optimize container size**: Smaller images = faster cold starts
4. **Use appropriate memory**: Don't over-allocate
5. **Implement caching**: Reduce compute time
6. **Use Cloud CDN**: For static assets

### Cost Estimation

```bash
# Estimate costs
# Cloud Run pricing calculator: https://cloud.google.com/run/pricing
# Typical costs:
# - CPU: $0.00002400 per vCPU-second
# - Memory: $0.00000250 per GiB-second
# - Requests: $0.40 per million requests
```

---

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/tips)
- [Container Registry Documentation](https://cloud.google.com/container-registry/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)

---

## Quick Reference

### Essential Commands

```bash
# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region $REGION \
    --allow-unauthenticated

# View logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME"

# Update service
gcloud run services update $SERVICE_NAME \
    --update-env-vars "KEY=value" \
    --region $REGION

# Get service URL
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
```

---

**Last Updated**: 2025-01-26

