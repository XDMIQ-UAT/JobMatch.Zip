# GTM Production Deployment Guide

## ✅ GTM Added to Production Configuration

GTM Container ID `GTM-KQV9THQ6` has been added to:

1. ✅ `docker-compose.prod.yml` - Frontend environment variables
2. ✅ `.github/workflows/deploy.yml` - GitHub Actions deployment
3. ✅ `scripts/deploy-to-vm.sh` - VM deployment script
4. ✅ `frontend/next.config.js` - Next.js configuration

## Deployment Steps

### Option 1: Docker Compose Deployment

**If deploying with docker-compose.prod.yml:**

```bash
# Rebuild and restart frontend
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

The GTM ID is now included in the frontend environment variables.

### Option 2: GitHub Actions Deployment

**If using GitHub Actions:**

The workflow has been updated to include `NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6` in the `.env` file created during deployment.

Just push your changes and the workflow will deploy with GTM included.

### Option 3: Manual VM Deployment

**If deploying manually to VM:**

1. SSH into your VM
2. Edit `.env` file:
   ```bash
   nano .env
   ```
3. Add:
   ```bash
   NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6
   ```
4. Rebuild frontend:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build frontend
   ```

## Verification After Deployment

### 1. Check GTM Code in HTML

1. Go to https://jobmatch.zip
2. Right-click → **View Page Source**
3. Search for: `googletagmanager.com/gtm.js`
4. Should see: `gtm.js?id=GTM-KQV9THQ6`

**If NOT found:**
- Environment variable not set correctly
- Need to rebuild/redeploy
- Check Docker logs: `docker logs jobmatch-frontend`

### 2. Check Browser Console

1. Open https://jobmatch.zip
2. Open DevTools (F12) → Console
3. Look for: "Google Tag Manager initialized"
4. Check Network tab for `gtm.js?id=GTM-KQV9THQ6` loading

### 3. Use GTM Preview Mode

1. Go to [GTM Dashboard](https://tagmanager.google.com/)
2. Select container: **GTM-KQV9THQ6**
3. Click **"Preview"** button
4. Enter: `https://jobmatch.zip`
5. Should connect and show GTM debugger

### 4. Publish GTM Container

**Important**: Container must be published for detection test to work.

1. Go to [GTM Dashboard](https://tagmanager.google.com/)
2. Select container: **GTM-KQV9THQ6**
3. Click **"Submit"** or **"Publish"** button
4. Create version name: "Initial Setup"
5. Click **"Publish"**
6. Wait 5-10 minutes

### 5. Retry Detection Test

1. Go to GTM Dashboard
2. Click **"Test your website"**
3. Enter: `https://jobmatch.zip`
4. Should now detect GTM ✅

## Troubleshooting

### GTM Code Not in HTML

**Check Docker logs:**
```bash
docker logs jobmatch-frontend
```

**Check environment variable:**
```bash
docker exec jobmatch-frontend env | grep GTM
```

Should show: `NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6`

**Rebuild frontend:**
```bash
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

### Container Not Detected

**Common causes:**
1. Container not published (must publish in GTM Dashboard)
2. Site not rebuilt after adding environment variable
3. Environment variable not set correctly
4. Need to wait 5-10 minutes after publishing

**Solutions:**
1. ✅ Publish container in GTM Dashboard
2. ✅ Rebuild and redeploy site
3. ✅ Verify environment variable is set
4. ✅ Wait 5-10 minutes, then retry

## Files Updated

- ✅ `docker-compose.prod.yml` - Added `NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6`
- ✅ `.github/workflows/deploy.yml` - Added to deployment `.env`
- ✅ `scripts/deploy-to-vm.sh` - Added to VM deployment script
- ✅ `frontend/next.config.js` - Added to Next.js env config

## Next Steps

1. ✅ **Rebuild and redeploy** your site
2. ✅ **Verify GTM code** appears in page source
3. ✅ **Publish GTM container** in GTM Dashboard
4. ✅ **Wait 5-10 minutes**, then retry detection test
5. ✅ **Set up GA4 tag** in GTM Dashboard (optional)

---

**Container ID**: GTM-KQV9THQ6  
**Site URL**: https://jobmatch.zip  
**Last Updated**: 2025-11-26

