# Google Tag Manager Quick Setup for jobmatch.zip

## ✅ Code Already Added

The GTM container code has been added to `frontend/app/layout.tsx`. You just need to:

1. **Get your GTM Container ID**
2. **Add it to `.env.local`**

## Multiple Sites? Use One Account, Multiple Containers

**Best Practice:**
- ✅ **One GTM Account** (create once, use for all sites)
- ✅ **One Container per Site** (each site gets its own Container ID)

**Example:**
```
GTM Account: "My Business"
├── jobmatch.zip → GTM-XXXXXXX
├── yourl.cloud → GTM-YYYYYYY
└── site3.com → GTM-ZZZZZZZ
```

See `docs/GTM_MULTI_SITE_SETUP.md` for multi-site setup guide.

## Step 1: Create GTM Account (One Time Only)

**If you already have a GTM account, skip to Step 2.**

1. Go to **[Google Tag Manager](https://tagmanager.google.com/)**
2. Sign in with your Google account
3. Click **"Create Account"**
4. Fill in:
   - **Account Name**: `Your Business Name` (e.g., "JobMatch Network")
   - **Country**: `United States`
5. Click **"Create"**

## Step 2: Create Container for This Site

1. In GTM Dashboard, click **"Add Container"** or **"Create Container"**
2. Fill in:
   - **Container Name**: `jobmatch.zip` (or your site domain)
   - **Container Type**: `Web`
3. Click **"Create"**

**💡 Tip**: Use the same GTM account for all your sites. Create one container per site.

## Step 3: Get Container ID

After creating, you'll see your **Container ID**:
- Format: `GTM-XXXXXXX`
- Example: `GTM-ABC1234`
- **Copy this ID** (each site has its own unique Container ID)

## Step 4: Add to Environment Variable

Create or update `.env.local` in project root:

```bash
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
```

Replace `GTM-XXXXXXX` with your actual Container ID.

## Step 5: Restart Dev Server

```bash
cd frontend
npm run dev
```

## Step 6: Verify

1. Open https://jobmatch.zip
2. Open browser DevTools (F12) → Console
3. Look for: "Google Tag Manager initialized"
4. Or use GTM Preview mode: [GTM Dashboard](https://tagmanager.google.com/) → Click "Preview"

## What Gets Tracked

✅ **Automatic Tracking**:
- Page views (all page navigations)
- Page URLs
- Page titles
- Browser information
- Device information
- Timestamp

✅ **Can Add Later**:
- Button clicks
- Form submissions
- Link clicks
- Scroll depth
- Video engagement
- Custom events

## Cost

✅ **100% FREE** - No limits, no credit card required

## Next Steps

After GTM is working:
1. Set up Google Analytics 4 (GA4) tag in GTM
2. Configure conversion tracking
3. Set up custom events
4. Add remarketing tags (if needed)

---

**Full Documentation**: 
- Single site: `docs/GTM_SETUP.md`
- Multiple sites: `docs/GTM_MULTI_SITE_SETUP.md`

**Setup Script**: `scripts/setup-gtm.ps1`

