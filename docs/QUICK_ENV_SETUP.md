# Quick Environment Variables Setup

## ✅ You've Added Variables to .env

Great! Now add these **Google OAuth** variables to complete the setup.

## Add to Your .env File

Add these lines to your `.env` file (located at `e:\zip-jobmatch\.env` or `e:\zip-jobmatch\backend\.env`):

```bash
# Google OAuth (ADD THESE)
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Stripe (You may already have these)
STRIPE_SECRET_KEY=sk_test_...  # or sk_live_... for production
STRIPE_WEBHOOK_SECRET=whsec_...  # Optional

# URLs (Optional - defaults provided)
FRONTEND_URL=https://jobmatch.zip
BACKEND_URL=http://localhost:8000  # or your backend URL
```

## Get Google OAuth Credentials

1. **Go to**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Create/Select Project**
3. **Enable API**: Google Identity API (or Google+ API)
4. **Create OAuth Credentials**:
   - Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
   - Application type: **Web application**
   - Name: **JobMatch Web Client**
   - **Authorized redirect URIs**:
     ```
     http://localhost:8000/api/auth/google/callback
     https://jobmatch.zip/api/auth/google/callback
     ```
5. **Copy**:
   - Client ID → `GOOGLE_OAUTH_CLIENT_ID`
   - Client Secret → `GOOGLE_OAUTH_CLIENT_SECRET`

## Verify Setup

After adding variables, run:

```bash
python scripts/verify-oauth-setup.py
```

You should see:
```
✅ GOOGLE_OAUTH_CLIENT_ID is set
✅ GOOGLE_OAUTH_CLIENT_SECRET is set
✅ STRIPE_SECRET_KEY is set
```

## Test It

1. **Start backend** (if not running):
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Test Google OAuth**:
   - Visit: `http://localhost:8000/api/auth/google/login`
   - Should redirect to Google sign-in

3. **After signing in**:
   - You'll be redirected to `/dashboard`
   - Check status: `http://localhost:8000/api/auth/google/status`

## What's Already Working

✅ Stripe variables detected  
✅ Backend configuration  
✅ Subscription system  
⏳ Google OAuth (add credentials above)

## Next Steps

1. ✅ Add Google OAuth credentials to .env
2. ✅ Run verification script
3. ✅ Test Google OAuth login
4. ✅ Test subscription flow

## Need Help?

- See full guide: [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md)
- Check setup: [ENV_SETUP_CHECKLIST.md](./ENV_SETUP_CHECKLIST.md)

