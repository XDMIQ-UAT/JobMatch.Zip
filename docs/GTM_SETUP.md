# Google Tag Manager Setup for JobMatch.zip

## Overview

Google Tag Manager (GTM) is a **free** tag management system that allows you to track:
- ✅ Site visits (page views)
- ✅ Clicks (button clicks, link clicks)
- ✅ Impressions (ad impressions, content views)
- ✅ Custom events (form submissions, downloads, etc.)
- ✅ Conversions (sign-ups, purchases, etc.)

**Cost**: Completely FREE - No limits on containers, tags, triggers, or events

## Quick Setup (5 Minutes)

### Step 1: Create GTM Account & Container

1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Sign in with your Google account
3. Click **"Create Account"**
4. Fill in:
   - **Account Name**: `JobMatch.zip`
   - **Country**: `United States`
   - **Container Name**: `jobmatch.zip`
   - **Container Type**: `Web`
5. Click **"Create"**

### Step 2: Get Container ID

After creating the container, you'll see your **Container ID**:
- Format: `GTM-XXXXXXX` (where X is alphanumeric)
- Example: `GTM-ABC1234`
- **Copy this ID** - you'll need it for the frontend

### Step 3: Configure Frontend

**Option A: Using Setup Script (Recommended)**

```powershell
# Run setup script
.\scripts\setup-gtm.ps1

# When prompted, enter your GTM Container ID (GTM-XXXXXXX)
```

**Option B: Manual Setup**

1. Create or update `.env.local` in project root:
```bash
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
```

2. Replace `GTM-XXXXXXX` with your actual Container ID

### Step 4: Verify Setup

1. **Restart Next.js dev server**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Check Browser Console**:
   - Open https://jobmatch.zip
   - Open browser DevTools (F12)
   - Check Console for GTM initialization
   - Look for: "Google Tag Manager initialized"

3. **Use GTM Preview Mode**:
   - Go to [GTM Dashboard](https://tagmanager.google.com/)
   - Click **"Preview"** button
   - Enter your site URL: `https://jobmatch.zip`
   - You should see GTM debugger connect

## What Gets Tracked Automatically

### Page Views
- ✅ All page navigations
- ✅ Route changes
- ✅ Page load events
- ✅ URL changes

### Built-in Variables (Available in GTM)
- Page URL
- Page Title
- Referrer
- Browser Information
- Device Information
- Timestamp

## Adding Custom Tracking

### Track Button Clicks

1. Go to GTM Dashboard → **Tags** → **New**
2. Tag Type: **Google Analytics: GA4 Event**
3. Configuration Tag: Select your GA4 configuration (or create one)
4. Event Name: `button_click`
5. Trigger: **Click - All Elements** (or create specific trigger)
6. Save and **Submit** changes

### Track Form Submissions

1. Go to GTM Dashboard → **Tags** → **New**
2. Tag Type: **Google Analytics: GA4 Event**
3. Event Name: `form_submit`
4. Trigger: **Form Submission**
5. Save and **Submit** changes

### Track Custom Events

In your frontend code, push events to dataLayer:

```typescript
// Track custom event
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'custom_event_name',
  event_category: 'engagement',
  event_label: 'button_click',
  value: 1
});
```

Then in GTM:
1. Create **Trigger** → **Custom Event**
2. Event name: `custom_event_name`
3. Create **Tag** → **Google Analytics: GA4 Event**
4. Link trigger to tag

## GTM Container Code Location

The GTM container code is added to `frontend/app/layout.tsx`:

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

**In `<body>` section (noscript fallback):**
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

## Privacy & Compliance

### GDPR Compliance

GTM respects user privacy:
- ✅ No personal data collected by default
- ✅ Cookie consent can be integrated
- ✅ User can opt-out via browser settings
- ✅ Respects Do Not Track headers

### Data Collection

By default, GTM collects:
- Page URLs (no PII)
- Page titles
- Referrer information
- Browser information (anonymized)
- Device information (anonymized)
- Timestamp

**No PII collected** unless explicitly configured in tags.

### Anonymous-First Architecture

GTM tracking aligns with our anonymous-first principles:
- ✅ No user identity tracking by default
- ✅ Anonymous IDs only
- ✅ No cross-site tracking (unless configured)
- ✅ Privacy-preserving by design

## Common Tracking Scenarios

### 1. Track Site Visits (Page Views)

**Automatic** - GTM tracks all page views by default.

To view in Google Analytics:
1. Create GA4 tag in GTM
2. Trigger: **All Pages**
3. Event: `page_view` (automatic)

### 2. Track Button Clicks

**Setup in GTM:**
1. Trigger: **Click - All Elements**
2. Condition: Click Element matches CSS selector (e.g., `button`, `.cta-button`)
3. Tag: **GA4 Event** with event name `button_click`

### 3. Track Link Clicks

**Setup in GTM:**
1. Trigger: **Click - All Elements**
2. Condition: Click Element = `a` (anchor tag)
3. Tag: **GA4 Event** with event name `link_click`

### 4. Track Form Submissions

**Setup in GTM:**
1. Trigger: **Form Submission**
2. Tag: **GA4 Event** with event name `form_submit`
3. Optional: Capture form data as event parameters

### 5. Track Scroll Depth

**Setup in GTM:**
1. Use **Scroll Depth** trigger
2. Configure: 25%, 50%, 75%, 100%
3. Tag: **GA4 Event** with event name `scroll_depth`

### 6. Track Video Engagement

**Setup in GTM:**
1. Use **YouTube Video** trigger
2. Track: Start, Progress, Complete
3. Tag: **GA4 Event** with event name `video_engagement`

## Integration with Google Analytics 4

### Setup GA4 Tag

1. Go to GTM Dashboard → **Tags** → **New**
2. Tag Type: **Google Analytics: GA4 Configuration**
3. Measurement ID: Your GA4 Measurement ID (G-XXXXXXXXXX)
4. Trigger: **All Pages**
5. Save and **Submit**

### Track Events to GA4

1. Create **GA4 Event** tag
2. Configuration Tag: Select your GA4 Configuration tag
3. Event Name: Your custom event name
4. Trigger: Your custom trigger
5. Save and **Submit**

## Troubleshooting

### GTM Not Loading

**Symptoms**: No GTM container in browser console

**Solutions**:
1. ✅ Check `.env.local` has `NEXT_PUBLIC_GTM_ID` set
2. ✅ Verify Container ID format: `GTM-XXXXXXX`
3. ✅ Restart Next.js dev server
4. ✅ Clear browser cache
5. ✅ Check browser console for errors

### Tags Not Firing

**Symptoms**: Events not appearing in GA4 or GTM debugger

**Solutions**:
1. ✅ Use GTM Preview mode to debug
2. ✅ Check trigger conditions
3. ✅ Verify tag configuration
4. ✅ Check browser console for errors
5. ✅ Ensure container is published (not just saved)

### Container ID Not Found

**Error**: "GTM container not found" or 404 errors

**Solutions**:
1. ✅ Verify Container ID is correct
2. ✅ Check Container ID format: `GTM-XXXXXXX`
3. ✅ Ensure container is published in GTM dashboard
4. ✅ Check container is not deleted or archived

### Environment Variable Not Working

**Symptoms**: GTM code not appearing in HTML

**Solutions**:
1. ✅ Check `.env.local` file exists (not `.env`)
2. ✅ Variable name: `NEXT_PUBLIC_GTM_ID` (must start with `NEXT_PUBLIC_`)
3. ✅ Restart Next.js dev server after adding variable
4. ✅ Check for typos in variable name

## Free Tier Information

✅ **GTM is completely free** with no limits on:
- Containers (unlimited)
- Tags (unlimited)
- Triggers (unlimited)
- Variables (unlimited)
- Events (unlimited)
- API calls (unlimited)

**No credit card required** - Just a Google account.

## Next Steps After Setup

1. ✅ **Set up GTM container** (done)
2. ✅ **Add GTM code to frontend** (done)
3. ⏳ **Configure Google Analytics 4 (GA4)** tag
4. ⏳ **Set up conversion tracking** (sign-ups, form submissions)
5. ⏳ **Configure custom events** (button clicks, downloads)
6. ⏳ **Set up remarketing tags** (if needed)
7. ⏳ **Configure e-commerce tracking** (if applicable)

## Resources

- [GTM Documentation](https://support.google.com/tagmanager/)
- [GTM Community](https://support.google.com/tagmanager/community)
- [GTM API Documentation](https://developers.google.com/tag-platform/tag-manager/api/v2)
- [GA4 Integration Guide](https://support.google.com/analytics/answer/9304153)

## Setup Script

Use the automated setup script:

```powershell
.\scripts\setup-gtm.ps1
```

This script will:
- Guide you through GTM setup
- Prompt for Container ID
- Add to `.env.local`
- Create documentation

---

**Setup Date**: 2025-11-26  
**Site URL**: https://jobmatch.zip  
**Status**: Ready for GTM Container ID

