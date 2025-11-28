# Deploy to https://jobmatch.zip

Complete guide for deploying the JobMatch platform to the custom domain `jobmatch.zip` using Google Cloud Run.

## Quick Start

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Domain Ownership** - You must own `jobmatch.zip`
3. **gcloud CLI** installed and authenticated
4. **Docker** installed and running

### One-Command Deployment

**Windows (PowerShell):**
```powershell
.\scripts\deploy-to-jobmatch-zip.ps1 -ProjectId "your-gcp-project-id"
```

**Linux/Mac (Bash):**
```bash
export GCP_PROJECT_ID="your-gcp-project-id"
chmod +x scripts/deploy-to-jobmatch-zip.sh
./scripts/deploy-to-jobmatch-zip.sh
```

---

## Architecture

### Services

- **Frontend Service**: `jobmatch-frontend` → `https://jobmatch.zip`
- **Backend Service**: `jobmatch-backend` → `https://api.jobmatch.zip`

### Infrastructure

- **Platform**: Google Cloud Run (serverless containers)
- **Region**: `us-central1` (configurable)
- **Frontend**: Vite + React Router (static site served via nginx)
- **Backend**: FastAPI/Python (containerized)

---

## Step-by-Step Deployment

### 1. Initial Setup

```bash
# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Or export as environment variable
export GCP_PROJECT_ID="your-project-id"
```

### 2. Verify Domain Ownership

Before mapping the domain, you must verify ownership:

```bash
gcloud domains verify jobmatch.zip
```

Follow the DNS verification instructions provided. This typically involves adding a TXT record to your domain's DNS settings.

### 3. Deploy Services

Run the deployment script:

**Windows:**
```powershell
.\scripts\deploy-to-jobmatch-zip.ps1 -ProjectId "your-project-id"
```

**Linux/Mac:**
```bash
./scripts/deploy-to-jobmatch-zip.sh
```

The script will:
- ✅ Build and push Docker images
- ✅ Deploy frontend to Cloud Run
- ✅ Deploy backend to Cloud Run
- ✅ Configure environment variables
- ✅ Set up CORS for the domain

### 4. Map Custom Domains

After deployment, map your custom domains:

```bash
# Map frontend domain
gcloud run domain-mappings create \
  --service=jobmatch-frontend \
  --domain=jobmatch.zip \
  --region=us-central1 \
  --project=YOUR_PROJECT_ID

# Map API subdomain
gcloud run domain-mappings create \
  --service=jobmatch-backend \
  --domain=api.jobmatch.zip \
  --region=us-central1 \
  --project=YOUR_PROJECT_ID
```

### 5. Update DNS Records

The domain mapping commands will output DNS records you need to add. Typically:

**For jobmatch.zip:**
- Type: `CNAME`
- Name: `@` or blank
- Value: `ghs.googlehosted.com.` (or provided value)

**For api.jobmatch.zip:**
- Type: `CNAME`
- Name: `api`
- Value: `ghs.googlehosted.com.` (or provided value)

Add these records at your domain registrar (where you registered jobmatch.zip).

### 6. Wait for SSL Certificate

Google Cloud Run automatically provisions SSL certificates. This can take **5-15 minutes**.

Check status:
```bash
gcloud run domain-mappings describe jobmatch.zip \
  --region=us-central1 \
  --project=YOUR_PROJECT_ID
```

---

## Environment Variables

### Backend Environment Variables

Set via Cloud Run:
```bash
gcloud run services update jobmatch-backend \
  --set-env-vars "FRONTEND_URL=https://jobmatch.zip" \
  --region=us-central1 \
  --project=YOUR_PROJECT_ID
```

### Frontend Environment Variables

Set during build (in `vite.config.ts` or build script):
- `VITE_API_URL=https://api.jobmatch.zip`

---

## Configuration Files

### Frontend Configuration

**`frontend/vite.config.ts`:**
```typescript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://api.jobmatch.zip',
        changeOrigin: true,
      },
    },
  },
})
```

### Backend CORS Configuration

**`backend/src/index.ts`:**
```typescript
app.use(cors({
  origin: [
    'https://jobmatch.zip',
    'https://www.jobmatch.zip',
    'http://localhost:3000' // for local dev
  ],
  credentials: true,
}));
```

---

## Deployment Options

### Deploy Only Frontend

```bash
# Windows
.\scripts\deploy-to-jobmatch-zip.ps1 -FrontendOnly

# Linux/Mac
FRONTEND_ONLY=true ./scripts/deploy-to-jobmatch-zip.sh
```

### Deploy Only Backend

```bash
# Windows
.\scripts\deploy-to-jobmatch-zip.ps1 -BackendOnly

# Linux/Mac
BACKEND_ONLY=true ./scripts/deploy-to-jobmatch-zip.sh
```

### Custom Region

```bash
# Windows
.\scripts\deploy-to-jobmatch-zip.ps1 -Region "us-east1"

# Linux/Mac
GCP_REGION="us-east1" ./scripts/deploy-to-jobmatch-zip.sh
```

---

## Post-Deployment

### Verify Deployment

1. **Check Frontend:**
   ```bash
   curl https://jobmatch.zip
   ```

2. **Check Backend:**
   ```bash
   curl https://api.jobmatch.zip/health
   ```

3. **Check Logs:**
   ```bash
   # Frontend logs
   gcloud run services logs read jobmatch-frontend --region=us-central1
   
   # Backend logs
   gcloud run services logs read jobmatch-backend --region=us-central1
   ```

### Update Services

To update after code changes:

```bash
# Just rebuild and redeploy
.\scripts\deploy-to-jobmatch-zip.ps1 -ProjectId "your-project-id"
```

---

## Troubleshooting

### Domain Not Resolving

1. **Check DNS records** - Ensure CNAME records are correct
2. **Wait for propagation** - DNS changes can take up to 48 hours
3. **Verify domain mapping:**
   ```bash
   gcloud run domain-mappings list --region=us-central1
   ```

### SSL Certificate Issues

1. **Check certificate status:**
   ```bash
   gcloud run domain-mappings describe jobmatch.zip --region=us-central1
   ```

2. **Wait longer** - SSL provisioning can take up to 15 minutes

3. **Verify DNS** - Certificate provisioning requires correct DNS records

### CORS Errors

1. **Check backend CORS configuration** - Ensure `https://jobmatch.zip` is in allowed origins
2. **Check environment variables** - Verify `FRONTEND_URL` is set correctly
3. **Check browser console** - Look for specific CORS error messages

### Service Not Starting

1. **Check logs:**
   ```bash
   gcloud run services logs read SERVICE_NAME --region=us-central1 --limit=50
   ```

2. **Check service status:**
   ```bash
   gcloud run services describe SERVICE_NAME --region=us-central1
   ```

3. **Verify Docker image:**
   ```bash
   docker run -p 8080:8080 gcr.io/PROJECT_ID/SERVICE_NAME:latest
   ```

---

## Cost Optimization

### Scaling Configuration

**Frontend:**
- Min instances: 1 (always on)
- Max instances: 5
- Memory: 512Mi
- CPU: 1

**Backend:**
- Min instances: 1 (always on)
- Max instances: 10
- Memory: 1Gi
- CPU: 2

### Cost Estimates

- **Frontend**: ~$10-20/month (1 instance always on)
- **Backend**: ~$20-40/month (1 instance always on)
- **Traffic**: $0.40 per million requests
- **Total**: ~$30-60/month for low-medium traffic

---

## Security

### Best Practices

1. **Environment Variables**: Never commit secrets to git
2. **CORS**: Only allow trusted origins
3. **HTTPS**: Always use HTTPS (automatic with Cloud Run)
4. **Authentication**: Use Cloud Run IAM for service-to-service auth
5. **Secrets**: Use Google Secret Manager for sensitive data

### Setting Up Secrets

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create SECRET_NAME --data-file=-

# Grant access to Cloud Run service
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Use in Cloud Run
gcloud run services update SERVICE_NAME \
  --set-secrets="ENV_VAR_NAME=SECRET_NAME:latest" \
  --region=us-central1
```

---

## Monitoring

### View Metrics

```bash
# Service metrics
gcloud run services describe SERVICE_NAME --region=us-central1

# Logs
gcloud run services logs read SERVICE_NAME --region=us-central1 --limit=100
```

### Set Up Alerts

Use Google Cloud Monitoring to set up alerts for:
- High error rates
- High latency
- Service unavailability
- Resource usage

---

## Rollback

If something goes wrong:

```bash
# List revisions
gcloud run revisions list --service=SERVICE_NAME --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region=us-central1
```

---

## Next Steps

After successful deployment:

1. ✅ Set up monitoring and alerts
2. ✅ Configure custom error pages
3. ✅ Set up CI/CD pipeline
4. ✅ Configure backup and disaster recovery
5. ✅ Set up staging environment

---

## Support

For issues or questions:
- Check Cloud Run logs
- Review Google Cloud documentation
- Check domain DNS settings
- Verify SSL certificate status

---

**Last Updated:** 2024-12-19  
**Maintained By:** DevOps Team

