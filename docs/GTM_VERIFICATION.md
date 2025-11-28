# GTM Verification Guide

## Quick Verification

Run the verification script:

```powershell
.\scripts\verify-gtm.ps1
```

## Manual Verification Steps

### 1. Check Environment Variables

**Root `.env.local`:**
```bash
NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6
```

**Frontend `.env.local`:**
```bash
NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6
```

### 2. Verify GTM Code in layout.tsx

The GTM code should be in `frontend/app/layout.tsx`:

**In `<head>` section:**
```tsx
{process.env.NEXT_PUBLIC_GTM_ID && (
  <script
    dangerouslySetInnerHTML={{
      __html: `
        (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','${process.env.NEXT_PUBLIC_GTM_ID}');
      `,
    }}
  />
)}
```

**In `<body>` section:**
```tsx
{process.env.NEXT_PUBLIC_GTM_ID && (
  <noscript>
    <iframe
      src={`https://www.googletagmanager.com/ns.html?id=${process.env.NEXT_PUBLIC_GTM_ID}`}
      height="0"
      width="0"
      style={{ display: 'none', visibility: 'hidden' }}
    />
  </noscript>
)}
```

### 3. Restart Dev Server

```bash
cd frontend
npm run dev
```

### 4. Browser Verification

#### Method 1: Console Check

1. Open https://jobmatch.zip
2. Open DevTools (F12)
3. Go to **Console** tab
4. Look for:
   - "Google Tag Manager initialized"
   - No GTM-related errors

#### Method 2: Network Tab

1. Open https://jobmatch.zip
2. Open DevTools (F12)
3. Go to **Network** tab
4. Refresh page
5. Look for:
   - `gtm.js?id=GTM-KQV9THQ6` - Should return 200 OK
   - `ns.html?id=GTM-KQV9THQ6` - Should return 200 OK

#### Method 3: GTM Preview Mode

1. Go to [GTM Dashboard](https://tagmanager.google.com/)
2. Select your container (GTM-KQV9THQ6)
3. Click **"Preview"** button
4. Enter your site URL: `https://jobmatch.zip`
5. Click **"Connect"**
6. You should see:
   - GTM debugger sidebar appears
   - Page view event fired
   - Container loaded successfully

#### Method 4: Check dataLayer

1. Open https://jobmatch.zip
2. Open DevTools (F12)
3. Go to **Console** tab
4. Type: `dataLayer`
5. Press Enter
6. You should see an array with GTM events

### 5. Verify GTM Container

1. Go to [GTM Dashboard](https://tagmanager.google.com/)
2. Select container: **GTM-KQV9THQ6**
3. Check:
   - Container is **Published** (not Draft)
   - Container name matches your site
   - Container type is **Web**

## Common Issues

### GTM Not Loading

**Symptoms:**
- No GTM script in Network tab
- Console shows errors
- dataLayer is undefined

**Solutions:**
1. ✅ Check `.env.local` has `NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6`
2. ✅ Restart Next.js dev server
3. ✅ Clear browser cache
4. ✅ Check Container ID is correct
5. ✅ Verify container is published in GTM

### Container ID Not Found

**Symptoms:**
- 404 errors for gtm.js
- "Container not found" errors

**Solutions:**
1. ✅ Verify Container ID: `GTM-KQV9THQ6`
2. ✅ Check container exists in GTM dashboard
3. ✅ Ensure container is published
4. ✅ Check container is not deleted/archived

### Environment Variable Not Working

**Symptoms:**
- GTM code not appearing in HTML source
- `process.env.NEXT_PUBLIC_GTM_ID` is undefined

**Solutions:**
1. ✅ Check `.env.local` file exists (not `.env`)
2. ✅ Variable name: `NEXT_PUBLIC_GTM_ID` (must start with `NEXT_PUBLIC_`)
3. ✅ Restart Next.js dev server after adding variable
4. ✅ Check for typos in variable name
5. ✅ Ensure no spaces around `=` sign

### GTM Preview Not Connecting

**Symptoms:**
- GTM Preview mode doesn't connect
- "Unable to connect" error

**Solutions:**
1. ✅ Check site URL is correct: `https://jobmatch.zip`
2. ✅ Ensure GTM code is loaded (check Network tab)
3. ✅ Try clearing browser cache
4. ✅ Check if site is accessible
5. ✅ Verify Container ID matches

## Verification Checklist

- [ ] `.env.local` file exists with `NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6`
- [ ] `frontend/.env.local` file exists with `NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6`
- [ ] GTM code is in `frontend/app/layout.tsx`
- [ ] Next.js dev server restarted
- [ ] Browser console shows no GTM errors
- [ ] Network tab shows `gtm.js?id=GTM-KQV9THQ6` loading successfully
- [ ] GTM Preview mode connects successfully
- [ ] `dataLayer` is defined in browser console
- [ ] Container is published in GTM dashboard

## Expected Results

### Browser Console
```
Google Tag Manager initialized
```

### Network Tab
```
gtm.js?id=GTM-KQV9THQ6    200 OK
ns.html?id=GTM-KQV9THQ6   200 OK
```

### GTM Preview Mode
```
✅ Container loaded
✅ Page view event fired
✅ Tags firing correctly
```

### dataLayer Check
```javascript
dataLayer
// Should return array with GTM events
[
  { gtm.start: 1234567890, event: "gtm.js" },
  { event: "page_view", ... }
]
```

## Next Steps After Verification

Once GTM is verified:

1. ✅ **Set up Google Analytics 4** tag in GTM
2. ✅ **Configure conversion tracking**
3. ✅ **Set up custom events** (button clicks, form submissions)
4. ✅ **Test all tags** in GTM Preview mode
5. ✅ **Publish container** in GTM dashboard

---

**Container ID**: GTM-KQV9THQ6  
**Last Verified**: 2025-11-26  
**Status**: Ready for verification

