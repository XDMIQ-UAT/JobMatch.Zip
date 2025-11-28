# Quick Test Guide - Google OAuth

## 🚀 Where to Test

### Method 1: Frontend Auth Page (Easiest)

1. **Make sure backend is running**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Make sure frontend is running**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser**:
   ```
   http://localhost:3000/auth
   ```

4. **Click the "Google" button** (🔍 icon)
   - Should redirect to Google sign-in
   - After signing in, redirects back to `/dashboard`

### Method 2: Direct Backend URL

1. **Make sure backend is running**

2. **Open your browser**:
   ```
   http://localhost:8000/api/auth/google/login
   ```

3. **Complete Google sign-in**
   - Redirects to Google
   - After sign-in, redirects to `/dashboard`

## ✅ What Should Happen

1. Click Google → Redirects to `accounts.google.com`
2. Sign in with Google → Google shows consent screen
3. Grant permission → Google redirects back
4. Backend processes → Creates anonymous ID
5. Sets session cookie → You're authenticated
6. Redirects to dashboard → `/dashboard?authenticated=true`

## 🔍 Verify It Worked

After signing in, check:

1. **URL**: Should be `/dashboard?authenticated=true`
2. **Cookies**: Check DevTools → Application → Cookies
   - Should see session cookie
3. **Status**: Visit `http://localhost:8000/api/auth/google/status`
   - Should show `{"linked": true, "provider": "google"}`

## 🐛 Troubleshooting

### "Google OAuth not configured"
- Run: `python scripts/verify-oauth-setup.py`
- Check `.env` has `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`

### "Invalid redirect_uri"
- Check Google Console → Credentials → OAuth 2.0 Client
- Add redirect URI: `http://localhost:8000/api/auth/google/callback`

### Backend not running
- Start it: `cd backend && python -m uvicorn main:app --reload`
- Check: `http://localhost:8000/health`

### Frontend not running
- Start it: `cd frontend && npm run dev`
- Check: `http://localhost:3000`

## 📝 Quick Commands

```bash
# Verify setup
python scripts/verify-oauth-setup.py

# Test backend endpoint
curl http://localhost:8000/api/auth/google/login

# Check status (after auth)
curl http://localhost:8000/api/auth/google/status
```

## 🎯 Test URLs

**Development:**
- Auth page: `http://localhost:3000/auth`
- Direct OAuth: `http://localhost:8000/api/auth/google/login`
- Status: `http://localhost:8000/api/auth/google/status`

**After auth:**
- Dashboard: `http://localhost:3000/dashboard`
- Home: `http://localhost:3000/`

