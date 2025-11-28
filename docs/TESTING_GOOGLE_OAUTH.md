# Testing Google OAuth - Quick Guide

## Where to Test

### Option 1: Frontend Auth Page (Recommended)

1. **Start the frontend** (if not running):
   ```bash
   cd frontend
   npm run dev
   ```

2. **Visit the auth page**:
   ```
   http://localhost:3000/auth
   ```

3. **Click "Google" button**:
   - Should redirect to Google sign-in
   - After signing in, redirects back to `/dashboard`

### Option 2: Direct Backend Endpoint

1. **Start the backend** (if not running):
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Visit Google OAuth endpoint**:
   ```
   http://localhost:8000/api/auth/google/login
   ```

3. **Complete Google sign-in**:
   - Redirects to Google
   - After sign-in, redirects to `/dashboard`

### Option 3: Test Script

Run the PowerShell test script:

```powershell
.\scripts\test-google-oauth.ps1
```

## Expected Flow

1. **Click Google button** → Redirects to Google
2. **Sign in with Google** → Google redirects back
3. **Backend processes** → Creates anonymous ID
4. **Sets session cookie** → Authenticated
5. **Redirects to dashboard** → `/dashboard?authenticated=true`

## Testing Checklist

- [ ] Frontend running on `http://localhost:3000`
- [ ] Backend running on `http://localhost:8000`
- [ ] Google OAuth credentials configured
- [ ] Visit `/auth` page
- [ ] Click Google button
- [ ] Complete Google sign-in
- [ ] Verify redirect to dashboard
- [ ] Check session cookie is set
- [ ] Verify anonymous_id is created

## Troubleshooting

### "Google OAuth not configured"
- Check `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in `.env`
- Run: `python scripts/verify-oauth-setup.py`

### "Invalid redirect_uri"
- Check redirect URI in Google Console matches:
  - `http://localhost:8000/api/auth/google/callback` (development)
  - `https://jobmatch.zip/api/auth/google/callback` (production)

### Redirects to wrong URL
- Check `FRONTEND_URL` and `BACKEND_URL` in `.env`
- Verify backend callback redirects to correct frontend URL

### Session not persisting
- Check browser allows cookies
- Verify session cookie is set (check DevTools → Application → Cookies)
- Check CORS settings allow credentials

## Quick Test URLs

**Development:**
- Auth page: `http://localhost:3000/auth`
- Direct OAuth: `http://localhost:8000/api/auth/google/login`
- Status check: `http://localhost:8000/api/auth/google/status`

**Production:**
- Auth page: `https://jobmatch.zip/auth`
- Direct OAuth: `https://api.jobmatch.zip/api/auth/google/login`
- Status check: `https://api.jobmatch.zip/api/auth/google/status`

## Next Steps After Testing

1. ✅ Verify Google OAuth works
2. ✅ Test subscription flow
3. ✅ Check subscription status endpoint
4. ✅ Verify anonymous identity is created
5. ✅ Test full user journey

