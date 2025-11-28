# How to Access the Subscribed Experience

## Quick Start

### Step 1: Authenticate with Google

1. Go to `https://jobmatch.zip/auth` (or `/auth` in development)
2. Click **"Sign in with Google"**
3. Grant permissions (we only use email, not your name)
4. You'll be redirected to `/dashboard` with an anonymous session

### Step 2: Subscribe

1. Once authenticated, go to `/dashboard`
2. Click **"Subscribe"** or **"Upgrade"**
3. You'll be redirected to Stripe Checkout ($1/month)
4. Complete payment
5. Redirected back to `/dashboard` with full access

## What You Get

### Subscribed Features

- ✅ **AI Job Matching Chat** - Full access to chat interface
- ✅ **Personalized Matching** - AI-powered job recommendations
- ✅ **Direct Messaging** - Contact hiring managers
- ✅ **Application Tracking** - Track your applications
- ✅ **Interview Prep** - AI-powered interview coaching
- ✅ **Career Insights** - Salary analytics and career guidance

### Free Features

- ✅ **Anonymous Identity** - Create account without revealing name
- ✅ **Google OAuth** - Quick sign-in with Google
- ✅ **Basic Platform Access** - Browse available features

## Technical Details

### Authentication Flow

```
User → Google OAuth → Anonymous ID Created → Session Cookie Set → Dashboard
```

### Subscription Flow

```
Authenticated User → Create Checkout Session → Stripe Checkout → 
Webhook Updates Status → Full Access Granted
```

### Zero-Knowledge Architecture

- **We DON'T store**: Your name, profile picture, or other PII
- **We DO store**: Email (for Stripe), locale (for language), anonymous_id
- **Your identity**: Completely anonymous - we can't link your account to your real identity

## API Endpoints

### Authentication

```bash
# Start Google OAuth
GET /api/auth/google/login

# Check auth status
GET /api/auth/google/status

# Check subscription status
GET /api/subscription/status-by-anonymous-id/{anonymous_id}
```

### Subscription

```bash
# Create checkout session
POST /api/subscription/create-checkout-session
{
  "anonymous_id": "your-anonymous-id"  # Optional - uses session if not provided
}

# Check subscription status
GET /api/subscription/status-by-anonymous-id/{anonymous_id}
```

## Frontend Integration Example

```typescript
// Check if user is authenticated and subscribed
async function checkAccess() {
  // Check Google auth status
  const authResponse = await fetch('/api/auth/google/status');
  const { linked, anonymous_id } = await authResponse.json();
  
  if (!linked) {
    // Redirect to auth
    window.location.href = '/api/auth/google/login';
    return;
  }
  
  // Check subscription status
  const subResponse = await fetch(`/api/subscription/status-by-anonymous-id/${anonymous_id}`);
  const { has_active_subscription } = await subResponse.json();
  
  if (!has_active_subscription) {
    // Show subscription prompt
    showSubscriptionPrompt();
    return;
  }
  
  // User has full access
  showFullDashboard();
}

// Create subscription checkout
async function subscribe() {
  const response = await fetch('/api/subscription/create-checkout-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include'  // Include session cookie
  });
  
  const { url } = await response.json();
  window.location.href = url;  // Redirect to Stripe
}
```

## Environment Setup

### Required Environment Variables

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Stripe
STRIPE_SECRET_KEY=sk_live_...  # or sk_test_... for testing
STRIPE_WEBHOOK_SECRET=whsec_...

# URLs
FRONTEND_URL=https://jobmatch.zip
BACKEND_URL=https://api.jobmatch.zip
```

## Testing

### Development

1. Use test Stripe keys (`sk_test_...`)
2. Use localhost URLs
3. Test with Google test accounts
4. Check console for OAuth state tokens

### Production

1. Use live Stripe keys (`sk_live_...`)
2. Configure production URLs
3. Set up Stripe webhook: `https://jobmatch.zip/api/subscription/webhook`
4. Test full flow end-to-end

## Troubleshooting

### "Not authenticated"
- Check session cookie is set
- Verify Google OAuth completed successfully
- Check browser allows cookies

### "No subscription found"
- Ensure user authenticated with Google (has email)
- Check Stripe customer was created
- Verify webhook processed subscription creation

### "Subscription status check failed"
- Verify anonymous_id is correct
- Check user has email linked to account
- Ensure Stripe API keys are correct

## Next Steps

1. ✅ Google OAuth implemented
2. ✅ Subscription system updated for anonymous_id
3. ✅ Subscription status endpoint created
4. ⏳ Frontend Google OAuth button (in progress)
5. ⏳ Frontend subscription flow integration

## Questions?

See:
- [Google OAuth Setup Guide](./GOOGLE_OAUTH_SETUP.md)
- [Stripe Configuration](./STRIPE_SETUP.md)
- [Anonymous Identity System](../business/identity-proxy/README.md)

