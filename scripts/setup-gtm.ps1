# Google Tag Manager Setup Script
# Sets up GTM for https://jobmatch.zip using gcloud

param(
    [string]$ProjectId = "futurelink-private-112912460",
    [string]$SiteUrl = "https://jobmatch.zip",
    [string]$ContainerName = "",
    [switch]$CreateContainer = $false
)

$ErrorActionPreference = "Continue"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Google Tag Manager Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Set project
Write-Host "Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Project set: $ProjectId" -ForegroundColor Green
Write-Host ""

# Note: GTM is a Google Marketing Platform service, not a GCP service
# GTM setup is done through Google Tag Manager web interface, not gcloud CLI
# However, we can use gcloud to:
# 1. Set up service account for GTM API access (if needed)
# 2. Configure credentials
# 3. Generate setup instructions

Write-Host "Google Tag Manager Setup Instructions:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "GTM is a free service from Google Marketing Platform." -ForegroundColor White
Write-Host "Setup is done through the web interface, not gcloud CLI." -ForegroundColor White
Write-Host ""
# Extract domain from SiteUrl for container name
if (-not $ContainerName) {
    $uri = [System.Uri]$SiteUrl
    $ContainerName = $uri.Host
}

Write-Host "Step 1: Create GTM Account (One Time Only)" -ForegroundColor Yellow
Write-Host "  If you already have a GTM account, skip to Step 2" -ForegroundColor Gray
Write-Host "  1. Go to: https://tagmanager.google.com/" -ForegroundColor White
Write-Host "  2. Sign in with your Google account" -ForegroundColor White
Write-Host "  3. Click 'Create Account' (only if you don't have one)" -ForegroundColor White
Write-Host "  4. Account Name: Your Business Name (e.g., JobMatch Network)" -ForegroundColor White
Write-Host "  5. Country: United States" -ForegroundColor White
Write-Host "  6. Click 'Create'" -ForegroundColor White
Write-Host ""
Write-Host "Step 2: Create Container for This Site" -ForegroundColor Yellow
Write-Host "  Site: $SiteUrl" -ForegroundColor Cyan
Write-Host "  Container Name: $ContainerName" -ForegroundColor Cyan
Write-Host "  1. In GTM Dashboard, click 'Add Container' or 'Create Container'" -ForegroundColor White
Write-Host "  2. Container Name: $ContainerName" -ForegroundColor White
Write-Host "  3. Container Type: Web" -ForegroundColor White
Write-Host "  4. Click 'Create'" -ForegroundColor White
Write-Host ""
Write-Host "  💡 TIP: Use ONE GTM Account for ALL your sites" -ForegroundColor Cyan
Write-Host "     Create ONE Container per site (separate Container ID per site)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 3: Get GTM Container ID" -ForegroundColor Yellow
Write-Host "  After creating container, you'll get a Container ID (GTM-XXXXXXX)" -ForegroundColor White
Write-Host "  Format: GTM-XXXXXXX (where X is alphanumeric)" -ForegroundColor White
Write-Host "  Each site gets its own unique Container ID" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 4: Add GTM to Frontend" -ForegroundColor Yellow
Write-Host "  The GTM container code is already in frontend/app/layout.tsx" -ForegroundColor White
Write-Host "  You just need to add the Container ID to .env.local" -ForegroundColor White
Write-Host ""

# Prompt for GTM Container ID
$gtmId = Read-Host "Enter your GTM Container ID (GTM-XXXXXXX) or press Enter to skip"

if ($gtmId -and $gtmId -match "^GTM-[A-Z0-9]+$") {
    Write-Host ""
    Write-Host "✅ Valid GTM Container ID: $gtmId" -ForegroundColor Green
    
    # Create environment variable file
    $envFile = ".env.local"
    $gtmVar = "NEXT_PUBLIC_GTM_ID=$gtmId"
    
    if (Test-Path $envFile) {
        $content = Get-Content $envFile -Raw
        if ($content -match "NEXT_PUBLIC_GTM_ID") {
            $content = $content -replace "NEXT_PUBLIC_GTM_ID=.*", $gtmVar
            Set-Content $envFile $content
            Write-Host "✅ Updated $envFile with GTM ID" -ForegroundColor Green
        } else {
            Add-Content $envFile "`n$gtmVar"
            Write-Host "✅ Added GTM ID to $envFile" -ForegroundColor Green
        }
    } else {
        Set-Content $envFile $gtmVar
        Write-Host "✅ Created $envFile with GTM ID" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. GTM code will be added to frontend/app/layout.tsx" -ForegroundColor White
    Write-Host "  2. Restart your Next.js dev server" -ForegroundColor White
    Write-Host "  3. Verify GTM is working: Check browser console for GTM events" -ForegroundColor White
    Write-Host "  4. Test in GTM Preview mode: https://tagmanager.google.com/" -ForegroundColor White
    Write-Host ""
} elseif ($gtmId) {
    Write-Host ""
    Write-Host "⚠️  Invalid GTM Container ID format. Expected: GTM-XXXXXXX" -ForegroundColor Yellow
    Write-Host "   You can add it manually later to .env.local as NEXT_PUBLIC_GTM_ID" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⏭️  Skipping GTM ID configuration. Add manually later:" -ForegroundColor Yellow
    Write-Host "   Add to .env.local: NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX" -ForegroundColor White
    Write-Host ""
}

# Create GTM setup documentation
$docPath = "docs\GTM_SETUP.md"
$docContent = @"
# Google Tag Manager Setup for JobMatch.zip

## Overview

Google Tag Manager (GTM) is a **free** tag management system that allows you to track:
- Site visits (page views)
- Clicks (button clicks, link clicks)
- Impressions (ad impressions, content views)
- Custom events (form submissions, downloads, etc.)
- Conversions (sign-ups, purchases, etc.)

## Setup Steps

### 1. Create GTM Account & Container

1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Sign in with your Google account
3. Click **"Create Account"**
4. Fill in:
   - **Account Name**: `JobMatch.zip`
   - **Country**: `United States`
   - **Container Name**: `jobmatch.zip`
   - **Container Type**: `Web`
5. Click **"Create"**

### 2. Get Container ID

After creating the container, you'll see your **Container ID**:
- Format: `GTM-XXXXXXX` (where X is alphanumeric)
- Example: `GTM-ABC1234`
- Copy this ID - you'll need it for the frontend

### 3. Configure Frontend

The GTM container code is already added to `frontend/app/layout.tsx`.

**Set Environment Variable:**

Create or update `.env.local`:
\`\`\`bash
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
\`\`\`

Replace `GTM-XXXXXXX` with your actual Container ID.

### 4. Verify Setup

1. **Restart Next.js dev server**:
   \`\`\`bash
   cd frontend
   npm run dev
   \`\`\`

2. **Check Browser Console**:
   - Open https://jobmatch.zip
   - Open browser DevTools (F12)
   - Check Console for GTM initialization messages
   - Look for: "Google Tag Manager initialized"

3. **Use GTM Preview Mode**:
   - Go to [GTM Dashboard](https://tagmanager.google.com/)
   - Click **"Preview"** button
   - Enter your site URL: `https://jobmatch.zip`
   - You should see GTM debugger connect

## Default Tracking

The GTM setup automatically tracks:

### Page Views
- All page navigations
- Route changes
- Page load events

### Clicks
- Button clicks
- Link clicks
- Form submissions

### Custom Events
- User interactions
- Form completions
- Button interactions

## Adding Custom Tags

### Example: Track Button Clicks

1. Go to GTM Dashboard
2. Click **Tags** → **New**
3. Tag Type: **Google Analytics: GA4 Event**
4. Configuration Tag: Select your GA4 configuration
5. Event Name: `button_click`
6. Trigger: **Click - All Elements** (or specific button)
7. Save and **Submit** changes

### Example: Track Form Submissions

1. Go to GTM Dashboard
2. Click **Tags** → **New**
3. Tag Type: **Google Analytics: GA4 Event**
4. Event Name: `form_submit`
5. Trigger: **Form Submission**
6. Save and **Submit** changes

## GTM Container Code

The GTM container code is added to `frontend/app/layout.tsx`:

\`\`\`tsx
{/* Google Tag Manager */}
{process.env.NEXT_PUBLIC_GTM_ID && (
  <>
    <script
      dangerouslySetInnerHTML={{
        __html: \`
          (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
          new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
          j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
          'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
          })(window,document,'script','dataLayer','\${process.env.NEXT_PUBLIC_GTM_ID}');
        \`,
      }}
    />
    <noscript>
      <iframe
        src={\`https://www.googletagmanager.com/ns.html?id=\${process.env.NEXT_PUBLIC_GTM_ID}\`}
        height="0"
        width="0"
        style={{ display: 'none', visibility: 'hidden' }}
      />
    </noscript>
  </>
)}
\`\`\`

## Privacy & Compliance

### GDPR Compliance

GTM respects user privacy:
- No personal data collected by default
- Cookie consent can be integrated
- User can opt-out via browser settings

### Data Collection

By default, GTM collects:
- Page URLs
- Page titles
- Referrer information
- Browser information
- Device information
- Timestamp

**No PII collected** unless explicitly configured.

## Troubleshooting

### GTM Not Loading

1. Check `.env.local` has `NEXT_PUBLIC_GTM_ID` set
2. Restart Next.js dev server
3. Clear browser cache
4. Check browser console for errors

### Tags Not Firing

1. Use GTM Preview mode to debug
2. Check trigger conditions
3. Verify tag configuration
4. Check browser console for errors

### Container ID Not Found

**Error**: "GTM container not found"

**Solution**:
1. Verify Container ID is correct
2. Check Container ID format: `GTM-XXXXXXX`
3. Ensure container is published in GTM dashboard

## Free Tier Limits

✅ **GTM is completely free** with no limits on:
- Containers
- Tags
- Triggers
- Variables
- Events

## Next Steps

1. ✅ Set up GTM container
2. ✅ Add GTM code to frontend
3. ⏳ Configure Google Analytics 4 (GA4) tag
4. ⏳ Set up conversion tracking
5. ⏳ Configure custom events
6. ⏳ Set up remarketing tags (if needed)

## Resources

- [GTM Documentation](https://support.google.com/tagmanager/)
- [GTM Community](https://support.google.com/tagmanager/community)
- [GTM API Documentation](https://developers.google.com/tag-platform/tag-manager/api/v2)

---

**Setup Date**: $(Get-Date -Format "yyyy-MM-dd")
**Site URL**: $SiteUrl
**Project**: $ProjectId
"@

Set-Content $docPath $docContent
Write-Host "✅ Created documentation: $docPath" -ForegroundColor Green
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Go to https://tagmanager.google.com/" -ForegroundColor White
Write-Host "  2. Create container for: $ContainerName" -ForegroundColor White
Write-Host "  3. Get your Container ID (GTM-XXXXXXX)" -ForegroundColor White
Write-Host "  4. Add to .env.local: NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX" -ForegroundColor White
Write-Host "  5. Restart Next.js dev server" -ForegroundColor White
Write-Host ""
Write-Host "💡 Multi-Site Setup:" -ForegroundColor Cyan
Write-Host "   - Use ONE GTM Account for all your sites" -ForegroundColor White
Write-Host "   - Create ONE Container per site" -ForegroundColor White
Write-Host "   - Each site gets its own Container ID" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - Single site: docs\GTM_SETUP.md" -ForegroundColor White
Write-Host "  - Multiple sites: docs\GTM_MULTI_SITE_SETUP.md" -ForegroundColor White

