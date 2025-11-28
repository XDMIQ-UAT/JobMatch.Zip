# Quick Start - Deploy to Google Cloud Run

## Prerequisites

✅ **Already configured:**
- Google Cloud Project: `futurelink-private-112912460`
- gcloud CLI: Installed and authenticated
- Docker: Installed (v28.0.1)
- Required APIs: Enabled

## Deploy Now

### Option 1: Use Deployment Script (Recommended)

```powershell
.\scripts\deploy-to-cloud-run.ps1
```

This script will:
1. ✅ Check prerequisites
2. 🔨 Build Docker image
3. 📤 Push to Google Container Registry
4. 🚀 Deploy to Cloud Run
5. ✅ Provide service URL

### Option 2: Manual Deployment

```powershell
# Set variables
$PROJECT_ID = "futurelink-private-112912460"
$SERVICE_NAME = "jobmatch-backend"
$REGION = "us-central1"
$IMAGE = "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

# Authenticate Docker
gcloud auth configure-docker

# Build image
docker build -f Dockerfile.cloudrun -t $IMAGE .

# Push image
docker push $IMAGE

# Deploy
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE `
    --platform managed `
    --region $REGION `
    --port 8080 `
    --memory 512Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10 `
    --timeout 300 `
    --allow-unauthenticated
```

## After Deployment

### Get Service URL
```powershell
gcloud run services describe jobmatch-backend --region us-central1 --format="value(status.url)"
```

### Test Health Endpoint
```powershell
$URL = gcloud run services describe jobmatch-backend --region us-central1 --format="value(status.url)"
curl "$URL/health"
```

### View Logs
```powershell
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=jobmatch-backend"
```

## Next Steps

1. **Set Environment Variables** (if needed):
   ```powershell
   gcloud run services update jobmatch-backend `
       --update-env-vars "ENV=production,LOG_LEVEL=info" `
       --region us-central1
   ```

2. **Configure Secrets** (for sensitive data):
   - See `docs/DEPLOYMENT_GCP_CLOUD_RUN.md` → Environment Variables section

3. **Set up Monitoring**:
   - View metrics in Cloud Console
   - Set up alerts for errors

4. **Configure Custom Domain** (optional):
   ```powershell
   gcloud run domain-mappings create --service jobmatch-backend --domain your-domain.com --region us-central1
   ```

## Troubleshooting

### Build Fails
- Check Dockerfile.cloudrun exists
- Verify backend/requirements.txt exists
- Check Docker has enough resources

### Deployment Fails
- Verify image was pushed: `gcloud container images list`
- Check logs: `gcloud logging read ...`
- Verify service account permissions

### Service Won't Start
- Check logs: `gcloud logging tail ...`
- Verify PORT environment variable (should be 8080)
- Check health endpoint: `/health`

## Full Documentation

See `docs/DEPLOYMENT_GCP_CLOUD_RUN.md` for complete guide including:
- Security best practices
- Environment variables
- Monitoring setup
- CI/CD integration
- Troubleshooting

