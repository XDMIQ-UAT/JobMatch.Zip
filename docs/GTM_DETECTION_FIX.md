# Fix: GTM Not Detected on Website

## Issue

Google Tag Manager detection test shows: **"Your Google tag wasn't detected on your website."**

## Common Causes & Solutions

### 1. Site Not Deployed / Only Localhost

**Problem**: GTM detection test works on **live websites**, not localhost.

**Solution**:
- ✅ Use **GTM Preview mode** for local testing
- ✅ Deploy site to production for detection test
- ✅ For production: Ensure `NEXT_PUBLIC_GTM_ID` is set in hosting platform

### 2. Environment Variable Not Set in Production

**Problem**: `.env.local` only works locally. Production needs environment variables set in hosting platform.

**Solution**:

#### For Vercel:
1. Go to Project Settings → Environment Variables
2. Add: `NEXT_PUBLIC_GTM_ID` = `GTM-KQV9THQ6`
3. Redeploy site

#### For Netlify:
1. Go to Site Settings → Environment Variables
2. Add: `NEXT_PUBLIC_GTM_ID` = `GTM-KQV9THQ6`
3. Redeploy site

#### For Other Platforms:
- Set `NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6` in hosting environment variables
- Rebuild and redeploy

### 3. Container Not Published

**Problem**: GTM container must be **published** for detection to work.

**Solution**:
1. Go to [GTM Dashboard](https://tagmanager.google.com/)
2. Select container: **GTM-KQV9THQ6**
3. Click **"Submit"** or **"Publish"**
4. Create version and publish
5. Wait 5-10 minutes
6. Retry detection test

### 4. Site Not Accessible

**Problem**: Site may be down or not accessible.

**Solution**:
- ✅ Check https://jobmatch.zip loads correctly
- ✅ Check SSL certificate is valid
- ✅ Check DNS is resolving correctly
- ✅ Check site is not behind maintenance mode

### 5. GTM Code Not in HTML

**Problem**: GTM code may not be rendering in production HTML.

**Solution**:
1. **View page source**: https://jobmatch.zip
2. **Search for**: `googletagmanager.com/gtm.js`
3. **Should see**: `gtm.js?id=GTM-KQV9THQ6`

**If NOT found**:
- Environment variable not set in production
- Need to rebuild/redeploy with environment variable

## Step-by-Step Fix

### Step 1: Verify GTM Code in Production HTML

1. Go to https://jobmatch.zip
2. Right-click → **View Page Source**
3. Search for: `GTM-KQV9THQ6` or `googletagmanager.com`
4. **If found**: Code is there, detection may just need time
5. **If NOT found**: Continue to Step 2

### Step 2: Set Environment Variable in Production

**For Vercel:**
```bash
# Via Vercel Dashboard:
# Project Settings → Environment Variables
# Add: NEXT_PUBLIC_GTM_ID = GTM-KQV9THQ6
# Redeploy
```

**For Netlify:**
```bash
# Via Netlify Dashboard:
# Site Settings → Environment Variables
# Add: NEXT_PUBLIC_GTM_ID = GTM-KQV9THQ6
# Redeploy
```

**For Other Platforms:**
- Set `NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6` in hosting environment
- Rebuild and redeploy

### Step 3: Publish GTM Container

1. Go to [GTM Dashboard](https://tagmanager.google.com/)
2. Select container: **GTM-KQV9THQ6**
3. Click **"Submit"** button
4. Enter version name: "Initial Setup"
5. Click **"Publish"**
6. Wait 5-10 minutes

### Step 4: Verify GTM Code is Loading

**Method 1: View Source**
- Go to https://jobmatch.zip
- View page source
- Search for `gtm.js?id=GTM-KQV9THQ6`
- Should appear in `<head>` section

**Method 2: Browser DevTools**
- Open https://jobmatch.zip
- Open DevTools (F12)
- Go to **Network** tab
- Refresh page
- Look for `gtm.js?id=GTM-KQV9THQ6`
- Should return **200 OK**

**Method 3: Console Check**
- Open https://jobmatch.zip
- Open DevTools (F12)
- Go to **Console** tab
- Type: `dataLayer`
- Should return array with GTM events

### Step 5: Retry Detection Test

1. Go to GTM Dashboard
2. Click **"Test your website"**
3. Enter: `https://jobmatch.zip`
4. Click **"Test"**
5. Should now detect GTM

## Quick Checklist

- [ ] GTM code appears in page source (View Source)
- [ ] `NEXT_PUBLIC_GTM_ID` set in production environment
- [ ] Site rebuilt/redeployed after setting environment variable
- [ ] GTM container is published (not draft)
- [ ] Site is accessible (https://jobmatch.zip loads)
- [ ] Waited 5-10 minutes after publishing container
- [ ] Checked Network tab for `gtm.js` loading successfully

## Alternative: Use GTM Preview Mode

**For local testing**, use GTM Preview mode instead of detection test:

1. Go to [GTM Dashboard](https://tagmanager.google.com/)
2. Select container: **GTM-KQV9THQ6**
3. Click **"Preview"** button
4. Enter: `http://localhost:3000` (for local) or `https://jobmatch.zip` (for production)
5. Click **"Connect"**
6. GTM debugger will appear showing all tags/events

**This works immediately** and doesn't require detection test.

## Still Not Working?

### Check GTM Container ID

Verify Container ID is correct:
- Go to GTM Dashboard
- Select container
- Check Container ID matches: `GTM-KQV9THQ6`

### Check Site URL

Verify site URL is correct:
- Detection test URL: `https://jobmatch.zip`
- No trailing slash
- HTTPS (not HTTP)

### Check Container Type

Verify container type is **Web**:
- Go to GTM Dashboard
- Select container
- Check container type is **Web** (not AMP, iOS, Android)

### Contact Support

If still not working:
1. Check GTM [Help Center](https://support.google.com/tagmanager/)
2. Check [GTM Community](https://support.google.com/tagmanager/community)
3. Verify all steps above completed

---

**Container ID**: GTM-KQV9THQ6  
**Site URL**: https://jobmatch.zip  
**Last Updated**: 2025-11-26

