# Google OAuth Setup for JobMatch.zip

## Overview

JobMatch uses Google OAuth for authentication while maintaining **zero-knowledge architecture**. We authenticate with Google but **do not store names** - only email and locale for functionality.

## Setup Instructions

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API** (or Google Identity API)
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen:
   - User Type: External
   - App name: JobMatch
   - Support email: your email
   - Scopes: `email`, `profile`, `openid`
   - Authorized domains: `jobmatch.zip`
6. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Name: JobMatch Web Client
   - Authorized redirect URIs:
     - `https://jobmatch.zip/api/auth/google/callback`
     - `http://localhost:8000/api/auth/google/callback` (for development)

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
FRONTEND_URL=https://jobmatch.zip
BACKEND_URL=https://api.jobmatch.zip  # or your backend URL
```

### 3. How It Works

#### Authentication Flow

1. User clicks "Sign in with Google"
2. Redirects to Google OAuth consent screen
3. User grants permission (email, profile)
4. Google redirects back with authorization code
5. Backend exchanges code for access token
6. Backend fetches user info from Google
7. **We extract ONLY email and locale** (NOT name)
8. Create/link anonymous identity
9. Set session cookie
10. Redirect to dashboard

#### Zero-Knowledge Architecture

- ✅ **Stored**: Email (for Stripe subscriptions), locale (for language preference)
- ❌ **NOT Stored**: Name, profile picture, or any other PII
- ✅ **Anonymous ID**: Cryptographically secure anonymous identifier
- ✅ **Session**: Secure HTTP-only cookie with anonymous_id

### 4. Frontend Integration

#### Basic Usage

```typescript
// Redirect to Google OAuth
window.location.href = '/api/auth/google/login';

// Or with custom redirect
window.location.href = '/api/auth/google/login?redirect_uri=/dashboard';
```

#### Check Authentication Status

```typescript
// Check if Google account is linked
const response = await fetch('/api/auth/google/status');
const { linked, provider, anonymous_id } = await response.json();
```

### 5. Subscription Integration

After Google OAuth, users can subscribe:

```typescript
// Create checkout session (uses anonymous_id from session)
const response = await fetch('/api/subscription/create-checkout-session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    anonymous_id: anonymous_id  // Optional - will use session if not provided
  })
});

const { url } = await response.json();
window.location.href = url;  // Redirect to Stripe Checkout
```

### 6. Check Subscription Status

```typescript
// Check subscription by anonymous_id
const response = await fetch(`/api/subscription/status-by-anonymous-id/${anonymous_id}`);
const { has_active_subscription, subscription } = await response.json();
```

## API Endpoints

### Google OAuth

- `GET /api/auth/google/login` - Initiate OAuth flow
- `GET /api/auth/google/callback` - Handle OAuth callback (internal)
- `GET /api/auth/google/status` - Check if Google account is linked

### Subscription

- `POST /api/subscription/create-checkout-session` - Create Stripe checkout
- `GET /api/subscription/status-by-anonymous-id/{anonymous_id}` - Check subscription status
- `GET /api/subscription/status/{customer_id}` - Check by Stripe customer ID
- `POST /api/subscription/cancel` - Cancel subscription
- `POST /api/subscription/webhook` - Stripe webhook handler

## Testing

### Development Mode

1. Use test Stripe keys: `STRIPE_SECRET_KEY=sk_test_...`
2. Use localhost redirect URIs
3. Check console logs for OAuth state tokens
4. Test with Google test accounts

### Production Checklist

- [ ] Google OAuth credentials configured
- [ ] Redirect URIs match production URLs
- [ ] Stripe webhook configured: `https://jobmatch.zip/api/subscription/webhook`
- [ ] Environment variables set in production
- [ ] HTTPS enabled (required for OAuth)
- [ ] Session cookies secure (HTTP-only, SameSite=Strict)

## Security Notes

1. **State Token**: Prevents CSRF attacks
2. **HTTPS Only**: OAuth requires HTTPS in production
3. **Session Cookies**: HTTP-only, secure, SameSite=Strict
4. **No Name Storage**: We don't store names, maintaining anonymity
5. **Email Only**: Email stored only for Stripe subscriptions (required by Stripe)

## Troubleshooting

### "Google OAuth not configured"
- Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Verify environment variables are loaded

### "Invalid redirect_uri"
- Check redirect URI matches exactly in Google Console
- Ensure protocol (http/https) matches
- Check for trailing slashes

### "Failed to exchange code for token"
- Verify client secret is correct
- Check redirect URI matches exactly
- Ensure code hasn't expired (codes expire quickly)

### Subscription Status Not Found
- Ensure user has authenticated with Google (has email)
- Check anonymous_id is correct
- Verify Stripe customer was created with email

## Next Steps

1. Set up Google OAuth credentials
2. Configure environment variables
3. Test authentication flow
4. Test subscription flow
5. Deploy to production

