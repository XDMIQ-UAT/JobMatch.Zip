# Quick Deployment Reference - jobmatch.zip

## 🚀 One-Command Deployment

### Windows (PowerShell)
```powershell
.\scripts\deploy-to-jobmatch-zip.ps1 -ProjectId "your-gcp-project-id"
```

### Linux/Mac (Bash)
```bash
export GCP_PROJECT_ID="your-gcp-project-id"
chmod +x scripts/deploy-to-jobmatch-zip.sh
./scripts/deploy-to-jobmatch-zip.sh
```

## 📋 Prerequisites Checklist

- [ ] Google Cloud account with billing enabled
- [ ] `gcloud` CLI installed and authenticated (`gcloud auth login`)
- [ ] Docker installed and running
- [ ] Domain `jobmatch.zip` registered and accessible
- [ ] GCP project created and set (`gcloud config set project PROJECT_ID`)

## 🔧 Pre-Deployment Steps

1. **Set GCP Project:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Verify Domain Ownership:**
   ```bash
   gcloud domains verify jobmatch.zip
   ```
   Follow DNS verification instructions.

## 🎯 Deployment Steps

1. **Run Deployment Script** (see commands above)

2. **Map Custom Domains:**
   ```bash
   # Frontend
   gcloud run domain-mappings create \
     --service=jobmatch-frontend \
     --domain=jobmatch.zip \
     --region=us-central1 \
     --project=YOUR_PROJECT_ID
   
   # Backend API
   gcloud run domain-mappings create \
     --service=jobmatch-backend \
     --domain=api.jobmatch.zip \
     --region=us-central1 \
     --project=YOUR_PROJECT_ID
   ```

3. **Update DNS Records:**
   - Add CNAME records as provided by domain mapping commands
   - Update at your domain registrar

4. **Wait for SSL (5-15 minutes):**
   ```bash
   gcloud run domain-mappings describe jobmatch.zip --region=us-central1
   ```

## 🌐 Final URLs

- **Frontend**: https://jobmatch.zip
- **Backend API**: https://api.jobmatch.zip

## 📚 Full Documentation

See `docs/DEPLOY_TO_JOBMATCH_ZIP.md` for complete guide.

