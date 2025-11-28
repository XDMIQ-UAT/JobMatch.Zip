# GTM Container ID Configuration

## Current Container ID

**Container ID**: `GTM-KQV9THQ6`

**Status**: ✅ Configured

## Location

The Container ID is stored in:
- `.env.local` (project root)
- `frontend/.env.local` (frontend directory)

## Verification

To verify GTM is working:

1. **Restart Next.js dev server**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Check browser console**:
   - Open https://jobmatch.zip
   - Open DevTools (F12) → Console
   - Look for: "Google Tag Manager initialized"

3. **Use GTM Preview mode**:
   - Go to [GTM Dashboard](https://tagmanager.google.com/)
   - Click "Preview" button
   - Enter: `https://jobmatch.zip`
   - You should see GTM debugger connect

## Updating Container ID

To change the Container ID:

1. Update `.env.local`:
   ```bash
   NEXT_PUBLIC_GTM_ID=GTM-NEWIDHERE
   ```

2. Restart Next.js dev server

3. Verify in browser console

## Multiple Sites

If you have multiple sites, each site should have its own Container ID:

```bash
# jobmatch.zip
NEXT_PUBLIC_GTM_ID=GTM-KQV9THQ6

# yourl.cloud (example)
NEXT_PUBLIC_GTM_ID=GTM-YYYYYYY
```

Each site's `.env.local` should have its own Container ID.

---

**Last Updated**: 2025-11-26  
**Container ID**: GTM-KQV9THQ6

