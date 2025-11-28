# Google Cloud Run - Quick Reference

## 🚀 Quick Deploy

```bash
# Set variables
export PROJECT_ID="your-project-id"
export SERVICE_NAME="your-service"
export REGION="us-central1"

# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region $REGION \
    --allow-unauthenticated
```

## 📋 Essential Commands

### Build & Push
```bash
# Cloud Build (recommended)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Local build & push
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .
gcloud auth configure-docker
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
```

### Deploy
```bash
# Basic deployment
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region $REGION \
    --allow-unauthenticated

# With options
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region $REGION \
    --memory 1Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --timeout 300 \
    --allow-unauthenticated
```

### Update
```bash
# Update image
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:v1.0.1 \
    --region $REGION

# Update env vars
gcloud run services update $SERVICE_NAME \
    --update-env-vars "KEY=value" \
    --region $REGION

# Update memory
gcloud run services update $SERVICE_NAME \
    --memory 1Gi \
    --region $REGION
```

### View & Debug
```bash
# Get service URL
gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format="value(status.url)"

# View logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME"

# List revisions
gcloud run revisions list --service $SERVICE_NAME --region $REGION

# Describe service
gcloud run services describe $SERVICE_NAME --region $REGION
```

## 🔐 Secrets Management

```bash
# Create secret
echo -n "secret-value" | gcloud secrets create SECRET_NAME --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding SECRET_NAME \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Use in deployment
gcloud run deploy $SERVICE_NAME \
    --set-secrets "ENV_VAR=SECRET_NAME:latest" \
    --region $REGION
```

## 🐳 Dockerfile Checklist

- [ ] Listens on `PORT` env var (default: 8080)
- [ ] Uses non-root user
- [ ] Includes health check
- [ ] Optimized for size (multi-stage if needed)
- [ ] Handles graceful shutdown

## ⚙️ Common Configurations

### Python/FastAPI
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 app:app
```

### Node.js/Express
```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
ENV PORT=8080
CMD ["node", "server.js"]
```

## 📊 Monitoring

```bash
# View metrics
gcloud monitoring time-series list \
    --filter='resource.type="cloud_run_revision"'

# Error reporting
# Automatically enabled - view in Console
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs: `gcloud logging tail ...` |
| Port not listening | Ensure app uses `PORT` env var |
| Cold start slow | Set `--min-instances 1` |
| Memory errors | Increase `--memory` |
| Timeout | Increase `--timeout` |

## 📚 Full Documentation

See [DEPLOYMENT_GCP_CLOUD_RUN.md](./DEPLOYMENT_GCP_CLOUD_RUN.md) for complete guide.

