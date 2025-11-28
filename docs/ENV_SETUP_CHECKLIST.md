# Environment Variables Setup Checklist

## ✅ Quick Verification

Run this command to check your setup:

```bash
python scripts/verify-oauth-setup.py
```

Or on Windows PowerShell:

```powershell
python scripts\verify-oauth-setup.py
```

## Required Variables

Add these to your `.env` file (in the project root: `e:\zip-jobmatch\.env`):

```bash
# Google OAuth (REQUIRED)
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

# Stripe (REQUIRED)
STRIPE_SECRET_KEY=sk_test_...  # Use sk_test_ for testing, sk_live_ for production
STRIPE_WEBHOOK_SECRET=whsec_...  # Optional - needed for webhooks

# URLs (Optional - defaults provided)
FRONTEND_URL=https://jobmatch.zip  # or http://localhost:3000 for dev
BACKEND_URL=https://api.jobmatch.zip  # or http://localhost:8000 for dev
```

## Where to Put .env File

The `.env` file should be in the **project root**:
```
e:\zip-jobmatch\.env
```

**NOT** in:
- `backend\.env` (won't be loaded by default)
- `frontend\.env` (different system)

## Getting Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Enable **Google+ API** or **Google Identity API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure:
   - **Application type**: Web application
   - **Name**: JobMatch Web Client
   - **Authorized redirect URIs**:
     - `https://jobmatch.zip/api/auth/google/callback` (production)
     - `http://localhost:8000/api/auth/google/callback` (development)
6. Copy the **Client ID** and **Client Secret**

## Getting Stripe Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Go to **Developers** → **API keys**
3. Copy:
   - **Publishable key**: `pk_test_...` (for frontend)
   - **Secret key**: `sk_test_...` (for backend - add to .env)
4. For webhooks:
   - Go to **Developers** → **Webhooks**
   - Add endpoint: `https://jobmatch.zip/api/subscription/webhook`
   - Copy the **Signing secret**: `whsec_...`

## Verification Steps

1. ✅ Run verification script: `python scripts/verify-oauth-setup.py`
2. ✅ Check all required variables show ✅
3. ✅ Test Google OAuth: Visit `/api/auth/google/login`
4. ✅ Test subscription: Create checkout session

## Common Issues

### Variables Not Loading

**Problem**: Script shows variables as NOT set even after adding to .env

**Solutions**:
- Make sure `.env` is in project root (`e:\zip-jobmatch\.env`)
- Check for typos in variable names (case-sensitive)
- Restart backend server after adding variables
- Check .env file encoding (should be UTF-8)

### Backend Can't Find Variables

**Problem**: Backend shows "Google OAuth not configured"

**Solutions**:
- Ensure `.env` file is in project root
- Check `backend/config.py` loads `.env` (it should)
- Restart backend: `cd backend && python -m uvicorn main:app --reload`
- Verify variables with: `python scripts/verify-oauth-setup.py`

### Google OAuth Redirect Error

**Problem**: "Invalid redirect_uri" error

**Solutions**:
- Check redirect URI in Google Console matches exactly:
  - `https://jobmatch.zip/api/auth/google/callback` (production)
  - `http://localhost:8000/api/auth/google/callback` (development)
- Ensure protocol matches (http vs https)
- Check for trailing slashes
- Verify BACKEND_URL environment variable is set correctly

## Testing

After setting up variables:

1. **Test Backend Health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Google OAuth Login**:
   ```bash
   # Should redirect to Google
   curl -L http://localhost:8000/api/auth/google/login
   ```

3. **Test Status Endpoint**:
   ```bash
   curl http://localhost:8000/api/auth/google/status
   ```

4. **Test Subscription** (after authenticating):
   ```bash
   curl -X POST http://localhost:8000/api/subscription/create-checkout-session \
     -H "Content-Type: application/json" \
     -d '{"anonymous_id": "your-anonymous-id"}'
   ```

## Next Steps

Once variables are set:

1. ✅ Run verification script
2. ✅ Start backend server
3. ✅ Test Google OAuth flow
4. ✅ Test subscription flow
5. ✅ Deploy to production

## Need Help?

- See [Google OAuth Setup Guide](./GOOGLE_OAUTH_SETUP.md)
- See [Subscribed Experience Access](./SUBSCRIBED_EXPERIENCE_ACCESS.md)
- Check backend logs for errors
- Verify environment variables are loaded: `python scripts/verify-oauth-setup.py`

