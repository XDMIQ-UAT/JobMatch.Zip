# VERCEL_PROJECT_ID Troubleshooting

## Problem: "VERCEL_PROJECT_ID is not set" Error

Even though you've set the secret, GitHub Actions can't find it. Here's how to fix it:

## Step 1: Verify Secret Name (Case-Sensitive!)

The secret name must be **exactly** `VERCEL_PROJECT_ID`:
- ✅ Correct: `VERCEL_PROJECT_ID`
- ❌ Wrong: `vercel_project_id` (lowercase)
- ❌ Wrong: `VERCEL_PROJECTID` (missing underscore)
- ❌ Wrong: `VERCEL_PROJECT_ID ` (trailing space)
- ❌ Wrong: ` VERCEL_PROJECT_ID` (leading space)

## Step 2: Check Secret Location

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Look for `VERCEL_PROJECT_ID` in the list
4. If you see it, click on it to verify:
   - Name is exactly `VERCEL_PROJECT_ID`
   - Value is not empty
   - No extra spaces or characters

## Step 3: Find Your Project ID

### Method 1: Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project (jobmatch.zip)
3. Go to **Settings** → **General**
4. Scroll down to find **Project ID**
5. Copy the entire ID (usually looks like: `prj_xxxxxxxxxxxxx`)

### Method 2: Vercel CLI
```bash
# Link your project (if not already linked)
vercel link

# Check the project.json file
cat .vercel/project.json

# Look for the "projectId" field
```

### Method 3: Vercel API
```bash
# List your projects
vercel projects ls

# Or use the API directly with your token
curl -H "Authorization: Bearer $VERCEL_TOKEN" \
  https://api.vercel.com/v9/projects
```

## Step 4: Recreate the Secret

If the secret exists but still isn't working:

1. **Delete the existing secret:**
   - Go to: Settings → Secrets and variables → Actions
   - Find `VERCEL_PROJECT_ID`
   - Click the delete/trash icon
   - Confirm deletion

2. **Create a new secret:**
   - Click **New repository secret**
   - Name: `VERCEL_PROJECT_ID` (copy-paste to avoid typos)
   - Value: Paste your Project ID (no quotes, no spaces)
   - Click **Add secret**

3. **Verify it was saved:**
   - You should see it in the secrets list
   - The name should be exactly `VERCEL_PROJECT_ID`

## Step 5: Check for Common Issues

### Issue: Secret Value is Empty
- Make sure you actually pasted a value
- Project ID should be a string like `prj_xxxxxxxxxxxxx`
- It should NOT be empty

### Issue: Extra Whitespace
- No leading spaces before the Project ID
- No trailing spaces after the Project ID
- No quotes around the Project ID

### Issue: Wrong Repository
- Make sure you're adding the secret to the **correct repository**
- Check the repository URL matches your project

### Issue: Organization vs Repository Secrets
- Repository secrets take precedence over organization secrets
- If you have both, make sure the repository secret is set correctly
- Consider removing the organization secret if it's conflicting

## Step 6: Test Locally

You can verify your Project ID works:

```bash
# Set your token
export VERCEL_TOKEN="your-token-here"
export VERCEL_PROJECT_ID="your-project-id-here"

# Test deployment (dry run)
vercel --prod --yes --debug
```

## Step 7: Re-run Workflow

After fixing the secret:

1. Go to **Actions** tab
2. Find the failed workflow run
3. Click **Re-run all jobs**
4. Or push a new commit to trigger a new run

## Still Not Working?

If the secret still isn't being found:

1. **Double-check the secret name** - Copy-paste `VERCEL_PROJECT_ID` exactly
2. **Verify the secret value** - Should be a non-empty string
3. **Check repository settings** - Make sure Actions are enabled
4. **Try a different approach** - Use Vercel's GitHub integration instead

## Alternative: Use Vercel GitHub Integration

Instead of manual secrets, you can use Vercel's built-in GitHub integration:

1. Go to Vercel Dashboard → Settings → Git
2. Connect your GitHub repository
3. Enable automatic deployments
4. This bypasses the need for manual `VERCEL_PROJECT_ID` secret

However, you'll still need `VERCEL_TOKEN` for CI/CD workflows.

