# Google Tag Manager Multi-Site Setup Guide

## Best Practice: One Account, Multiple Containers

**Recommended Structure:**
- ✅ **One GTM Account** (e.g., "My Business" or "JobMatch Network")
- ✅ **One Container per Site** (each site gets its own container)

### Why This Structure?

**Benefits:**
1. **Better Organization** - Each site has its own container
2. **Site-Specific Tracking** - Clean data separation
3. **Easier Management** - Manage each site independently
4. **Better Security** - Grant access per container
5. **Cleaner Analytics** - No cross-site data mixing
6. **Easier Debugging** - Isolate issues per site

**Example Structure:**
```
GTM Account: "JobMatch Network"
├── Container: jobmatch.zip (GTM-XXXXXXX)
├── Container: yourl.cloud (GTM-YYYYYYY)
├── Container: another-site.com (GTM-ZZZZZZZ)
└── Container: yet-another-site.com (GTM-AAAAAAA)
```

## Setup Process for Multiple Sites

### Step 1: Create GTM Account (One Time)

1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Click **"Create Account"**
3. Fill in:
   - **Account Name**: `Your Business Name` or `JobMatch Network`
   - **Country**: `United States`
4. Click **"Create"**

**Note**: You only create the account once. All containers go under this account.

### Step 2: Create Container for Each Site

For **each site**, create a separate container:

#### Container 1: jobmatch.zip

1. In GTM Dashboard, click **"Add Container"** or **"Create Container"**
2. Fill in:
   - **Container Name**: `jobmatch.zip`
   - **Container Type**: `Web`
3. Click **"Create"**
4. **Copy Container ID**: `GTM-XXXXXXX`
5. Add to `.env.local`:
   ```bash
   NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
   ```

#### Container 2: yourl.cloud (or other site)

1. In same GTM account, click **"Add Container"**
2. Fill in:
   - **Container Name**: `yourl.cloud`
   - **Container Type**: `Web`
3. Click **"Create"**
4. **Copy Container ID**: `GTM-YYYYYYY`
5. Add to that site's `.env.local`:
   ```bash
   NEXT_PUBLIC_GTM_ID=GTM-YYYYYYY
   ```

#### Repeat for Each Site

Create a container for each site you manage.

## Managing Multiple Containers

### View All Containers

1. Go to [GTM Dashboard](https://tagmanager.google.com/)
2. You'll see all containers listed
3. Click on any container to manage it

### Switch Between Containers

1. In GTM Dashboard, click the container dropdown (top left)
2. Select the container you want to manage
3. All tags, triggers, and variables are container-specific

### Container-Specific Configuration

Each container can have:
- ✅ Different tags (GA4, Facebook Pixel, etc.)
- ✅ Different triggers
- ✅ Different variables
- ✅ Different environments (Dev, Staging, Production)
- ✅ Different user permissions

## Environment Variables per Site

### Option 1: Separate .env.local Files (Recommended)

**For jobmatch.zip:**
```bash
# .env.local in jobmatch.zip project
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
```

**For yourl.cloud:**
```bash
# .env.local in yourl.cloud project
NEXT_PUBLIC_GTM_ID=GTM-YYYYYYY
```

### Option 2: Shared Configuration File

If managing multiple sites from one codebase:

```bash
# .env.local
NEXT_PUBLIC_GTM_ID_JOBMATCH=GTM-XXXXXXX
NEXT_PUBLIC_GTM_ID_YOURL=GTM-YYYYYYY
NEXT_PUBLIC_GTM_ID_ANOTHER=GTM-ZZZZZZZ

# Then in code, use based on site:
const gtmId = process.env.NEXT_PUBLIC_GTM_ID_JOBMATCH; // for jobmatch.zip
```

## Quick Setup Script for Multiple Sites

### Automated Setup

```powershell
# Setup GTM for jobmatch.zip
.\scripts\setup-gtm.ps1 -SiteUrl "https://jobmatch.zip"

# Setup GTM for yourl.cloud
.\scripts\setup-gtm.ps1 -SiteUrl "https://yourl.cloud"

# Setup GTM for another site
.\scripts\setup-gtm.ps1 -SiteUrl "https://another-site.com"
```

### Manual Setup Checklist

For each site:
- [ ] Create container in GTM account
- [ ] Copy Container ID (GTM-XXXXXXX)
- [ ] Add to site's `.env.local`
- [ ] Verify GTM code in site's layout.tsx
- [ ] Test with GTM Preview mode
- [ ] Publish container

## Container Naming Convention

**Recommended naming:**
- Use domain name: `jobmatch.zip`
- Use subdomain if needed: `app.jobmatch.zip`
- Use environment: `jobmatch.zip-prod`, `jobmatch.zip-staging`

**Examples:**
```
jobmatch.zip          → GTM-XXXXXXX
yourl.cloud           → GTM-YYYYYYY
app.jobmatch.zip      → GTM-ZZZZZZZ
staging.jobmatch.zip  → GTM-AAAAAAA
```

## Sharing Containers vs Separate Containers

### ✅ Use Separate Containers When:
- Sites have different purposes
- Different teams manage different sites
- Different tracking requirements
- Need to isolate data
- Different security requirements

### ⚠️ Consider Shared Container When:
- Sites are subdomains of same domain
- Same team manages all sites
- Same tracking requirements
- Want unified analytics

**For most cases**: **Separate containers** is recommended.

## Cost

✅ **Still 100% FREE** - No matter how many containers you have:
- Unlimited containers per account
- Unlimited tags per container
- Unlimited triggers per container
- Unlimited events per container

## Access Control

### Grant Access Per Container

1. Go to GTM Dashboard
2. Select container
3. Click **Admin** → **User Management**
4. Click **Add Users**
5. Enter email and select permission level:
   - **View**: Can view but not edit
   - **Edit**: Can edit tags/triggers
   - **Approve**: Can approve changes
   - **Publish**: Can publish changes
6. Click **Invite**

**Benefits**:
- Team member can access jobmatch.zip container but not yourl.cloud
- Different permissions per container
- Better security

## Common Multi-Site Scenarios

### Scenario 1: Multiple Domains

**Sites**: jobmatch.zip, yourl.cloud, another-site.com

**Setup**:
- One GTM Account: "My Business"
- Three Containers: One per domain
- Each site uses its own Container ID

### Scenario 2: Subdomains

**Sites**: app.jobmatch.zip, admin.jobmatch.zip, api.jobmatch.zip

**Options**:
- **Option A**: One container for all subdomains (shared tracking)
- **Option B**: Separate containers per subdomain (isolated tracking)

**Recommendation**: Option A (shared) if same team/tracking needs

### Scenario 3: Staging + Production

**Sites**: jobmatch.zip (prod), staging.jobmatch.zip (staging)

**Setup**:
- One GTM Account
- Two Containers: `jobmatch.zip-prod`, `jobmatch.zip-staging`
- Use different Container IDs per environment

## Quick Reference

### Create New Container

1. GTM Dashboard → **Add Container**
2. Name: `your-site.com`
3. Type: `Web`
4. Copy Container ID
5. Add to site's `.env.local`

### List All Containers

GTM Dashboard shows all containers in your account.

### Delete Container

1. GTM Dashboard → Select container
2. **Admin** → **Container Settings**
3. Scroll down → **Delete Container**
4. Type container name to confirm

**Warning**: Deleting container removes all tags/triggers/data. Cannot be undone.

## Summary

**For Multiple Sites:**
- ✅ **One GTM Account** (create once)
- ✅ **One Container per Site** (create per site)
- ✅ **Each site gets its own Container ID**
- ✅ **Each site uses its own Container ID in .env.local**
- ✅ **100% FREE** - No matter how many containers

**Example:**
```
GTM Account: "JobMatch Network"
├── jobmatch.zip → GTM-XXXXXXX → NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
├── yourl.cloud → GTM-YYYYYYY → NEXT_PUBLIC_GTM_ID=GTM-YYYYYYY
└── site3.com → GTM-ZZZZZZZ → NEXT_PUBLIC_GTM_ID=GTM-ZZZZZZZ
```

---

**Setup Date**: 2025-11-26  
**Cost**: FREE (unlimited containers)  
**Documentation**: `docs/GTM_SETUP.md` for single site setup

