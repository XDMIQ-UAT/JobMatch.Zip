# Vercel Token Setup Guide

## Quick Fix: Invalid Token Error

If you're seeing `Error: The specified token is not valid`, follow these steps:

## Step 1: Generate a New Vercel Token

1. Go to [Vercel Account Tokens](https://vercel.com/account/tokens)
2. Click **Create Token**
3. Name it: `github-actions-jobmatch`
4. **Scope**: Select **Full Account** (not just a project)
5. Click **Create**
6. **IMPORTANT**: Copy the token immediately - you won't see it again!

## Step 2: Add Token to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `VERCEL_TOKEN` (exactly, case-sensitive)
5. Value: Paste the token you copied (no spaces, no quotes)
6. Click **Add secret**

## Step 3: Verify Token Format

The token should:
- ✅ Start with `vercel_` or similar prefix
- ✅ Be a long string (usually 40+ characters)
- ✅ Have NO leading/trailing spaces
- ✅ Have NO quotes around it
- ✅ Be on a single line

**Common mistakes:**
- ❌ Adding quotes: `"vercel_abc123..."` → Remove quotes
- ❌ Extra spaces: ` vercel_abc123... ` → Remove spaces
- ❌ Multiple lines: Token split across lines → Single line only

## Step 4: Verify Other Secrets

Also verify these secrets exist:

- **`VERCEL_TEAM_ID`**: Your Vercel Team ID
  - Find it: Vercel Dashboard → Settings → General → Team ID
  - Or run locally: `vercel whoami` and check account settings

- **`VERCEL_PROJECT_ID`**: Your Vercel Project ID
  - Find it: Vercel Dashboard → Your Project → Settings → General → Project ID
  - Or run locally: `vercel link` and check `.vercel/project.json`

## Step 5: Test Token Locally (Optional)

Test if your token works:

```bash
# Set token temporarily
export VERCEL_TOKEN="your-token-here"

# Test authentication
vercel whoami

# Should show your account info
```

## Step 6: Re-run Workflow

1. Go to **Actions** tab
2. Find the failed workflow run
3. Click **Re-run all jobs**
4. Or push a new commit to trigger a new run

## Troubleshooting

### Token Still Not Working?

1. **Regenerate the token** - Old tokens might be expired
2. **Check token scope** - Must be "Full Account" not just project scope
3. **Verify secret name** - Must be exactly `VERCEL_TOKEN` (case-sensitive)
4. **Check for whitespace** - Copy token again, ensure no extra spaces
5. **Verify token format** - Should start with `vercel_` prefix

### Check Secret Values (Without Exposing Them)

The workflow now includes a verification step that checks if secrets are set (without exposing their values).

### Token Permissions

The token needs these permissions:
- ✅ Read projects
- ✅ Deploy projects
- ✅ Read team information

If using a team account, ensure the token has team-level access.

## Alternative: Use Vercel CLI Login

If tokens aren't working, you can also use Vercel's GitHub integration:

1. Go to Vercel Dashboard → Settings → Git
2. Connect your GitHub repository
3. Enable automatic deployments
4. This bypasses the need for manual tokens

However, the GitHub Actions workflow still needs a token for CI/CD.

## Still Having Issues?

1. Check workflow logs for the exact error message
2. Verify all three secrets are set: `VERCEL_TOKEN`, `VERCEL_TEAM_ID`, `VERCEL_PROJECT_ID`
3. Try regenerating all three values
4. Check Vercel dashboard for any account/team restrictions

