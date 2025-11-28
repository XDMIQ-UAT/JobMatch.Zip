# Stripe Checkout Fix - Resolved ✅

## Problem
Checkout was failing because Next.js frontend couldn't reach the FastAPI backend.

## Root Cause
**It was our code, not Stripe.**

The frontend was calling `/api/subscription/create-checkout-session` but:
- Next.js serves on port 3000
- FastAPI backend serves on port 8000
- No API proxy route existed to bridge them

## Solution Applied
Created Next.js API route proxy at:
```
frontend/app/api/subscription/create-checkout-session/route.ts
```

This proxies frontend requests to the backend automatically.

## Configuration Updates

### 1. Created API Proxy Route ✅
- Location: `frontend/app/api/subscription/create-checkout-session/route.ts`
- Function: Forwards requests from Next.js to FastAPI backend
- Handles errors gracefully

### 2. Fixed Backend Port ✅
- Updated `next.config.js` from port 4000 → 8000
- Ensures proxy routes to correct backend

### 3. Added Stripe Environment Variables ✅
- Updated `backend/.env` with Stripe configuration
- **ACTION REQUIRED**: Replace placeholder keys with real Stripe test keys

## Next Steps

### 1. Get Your Stripe Test Keys
```bash
# Visit Stripe Dashboard
https://dashboard.stripe.com/test/apikeys

# Copy your test keys:
# - Secret key (sk_test_...)
# - Publishable key (pk_test_...)
```

### 2. Update Backend .env
```bash
# Edit: E:\JobFinder\backend\.env
STRIPE_SECRET_KEY=sk_test_YOUR_ACTUAL_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
FRONTEND_URL=http://localhost:3000
```

### 3. Install Backend Dependencies
```powershell
cd E:\JobFinder\backend
pip install stripe==7.8.0
```

### 4. Test the Flow

**Terminal 1 - Backend:**
```powershell
cd E:\JobFinder\backend
python main.py
# Should start on http://localhost:8000
```

**Terminal 2 - Frontend:**
```powershell
cd E:\JobFinder\frontend
npm run dev
# Should start on http://localhost:3000
```

**Terminal 3 - Stripe Webhook (Optional for local testing):**
```powershell
stripe listen --forward-to http://localhost:8000/api/subscription/webhook
# Copy the webhook secret (whsec_...) to .env
```

### 5. Test Checkout
1. Visit: http://localhost:3000
2. Enter email address
3. Click "Subscribe Now"
4. Should redirect to Stripe Checkout page

### Test Cards (Stripe Test Mode)
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Auth**: `4000 0025 0000 3155`
- Any future date for expiry
- Any 3 digits for CVC
- Any 5 digits for ZIP

## Verification Checklist

- [x] API proxy route created
- [x] Backend port fixed in config
- [x] Environment variables template added
- [ ] Stripe test keys configured (replace YOUR_KEY_HERE)
- [ ] Backend dependencies installed
- [ ] Both servers running
- [ ] Checkout flow tested end-to-end

## Architecture Flow

```
User Browser (localhost:3000)
    ↓
Next.js Frontend
    ↓ /api/subscription/create-checkout-session
Next.js API Proxy Route
    ↓ http://localhost:8000/api/subscription/create-checkout-session
FastAPI Backend
    ↓ Stripe API
Stripe Checkout Session
    ↓ Redirect
Stripe Hosted Checkout Page
```

## Common Issues

### "Failed to create checkout session"
- Check backend is running on port 8000
- Verify STRIPE_SECRET_KEY in backend/.env
- Check browser console for errors

### CORS Errors
- Backend already has CORS middleware configured
- Ensure `allow_origins` includes http://localhost:3000

### Webhook Signature Error
- Only relevant for production
- For local testing, use `stripe listen` command
- Update STRIPE_WEBHOOK_SECRET with value from CLI

## Production Deployment

When deploying to jobmatch.zip:

1. **Switch to Live Mode**
   - Get live Stripe keys (pk_live_, sk_live_)
   - Update all environment variables

2. **Update URLs**
   ```env
   FRONTEND_URL=https://jobmatch.zip
   ```

3. **Configure Webhook in Stripe Dashboard**
   - Add endpoint: https://jobmatch.zip/api/subscription/webhook
   - Select events: All subscription events
   - Copy webhook secret to production .env

4. **Test with Real Card**
   - Use small amount first
   - Verify webhook events received
   - Check customer portal works

## Support

- Stripe Dashboard: https://dashboard.stripe.com/test
- Stripe Docs: https://stripe.com/docs/billing/subscriptions/overview
- Issue? Check logs: Browser Console + Backend Terminal

---

**Status**: ✅ Fixed - Ready for testing with real Stripe keys
**Date**: November 24, 2025
**Next Action**: Add your Stripe test keys to backend/.env and test the flow
