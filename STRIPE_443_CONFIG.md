# Stripe Checkout - Port 443 Configuration ✅

## Overview
Stripe checkout now configured to use **HTTPS on port 443 only** for external communications, with internal services on ports 8000/3000.

## Configuration Complete

### 1. Backend Configuration ✅
**File**: `backend/.env`
```env
FRONTEND_URL=https://jobmatch.zip
STRIPE_WEBHOOK_SECRET=whsec_i9tvC6C4LTmEKC2QioHbKOwxuyOtghkB
```

- Backend runs internally on **port 8000**
- NGINX proxies external port **443** → internal port **8000**
- Stripe webhooks configured for `https://jobmatch.zip/api/subscription/webhook`

### 2. Frontend Configuration ✅
**File**: `frontend/app/api/subscription/create-checkout-session/route.ts`
```typescript
const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'production' ? 'https://jobmatch.zip' : 'http://localhost:8000');
```

- Frontend runs internally on **port 3000**
- NGINX proxies external port **443** → internal port **3000**
- API calls use HTTPS for production

### 3. Stripe Webhook Endpoint ✅
**Created via CLI**:
```bash
Webhook ID: we_1SX0wsBObYs4DzR45k3wGTNy
URL: https://jobmatch.zip/api/subscription/webhook
Secret: whsec_i9tvC6C4LTmEKC2QioHbKOwxuyOtghkB
```

**Events monitored**:
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `checkout.session.completed`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

### 4. NGINX Configuration ✅
**File**: `nginx-jobmatch.conf`

External traffic flow:
```
User Browser (HTTPS:443)
    ↓
NGINX (Port 443 with SSL)
    ↓ /api/* → localhost:8000
    ↓ /* → localhost:3000
Backend/Frontend (Internal ports)
```

## Architecture

### Port Mapping
| Service | Internal Port | External Port | Protocol |
|---------|--------------|---------------|----------|
| Frontend (Next.js) | 3000 | 443 (HTTPS) | Via NGINX |
| Backend (FastAPI) | 8000 | 443 (HTTPS) | Via NGINX |
| Stripe Webhooks | N/A | 443 (HTTPS) | Direct to /api/subscription/webhook |

### URL Structure
- **Production Frontend**: `https://jobmatch.zip` (port 443)
- **Production API**: `https://jobmatch.zip/api/*` (port 443)
- **Stripe Checkout Success**: `https://jobmatch.zip/subscription/success`
- **Stripe Checkout Cancel**: `https://jobmatch.zip/subscription/cancelled`

## Testing the Configuration

### Test Checkout Flow (CLI Only)

1. **Start Backend** (internal port 8000):
```powershell
cd E:\JobFinder\backend
python main.py
```

2. **Start Frontend** (internal port 3000):
```powershell
cd E:\JobFinder\frontend
npm run dev
```

3. **Test Checkout API via curl**:
```powershell
# Test checkout session creation
curl -X POST https://jobmatch.zip/api/subscription/create-checkout-session `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com"}'
```

Expected response:
```json
{
  "session_id": "cs_test_...",
  "url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "subscription_count": 1,
  "max_subscriptions": 999
}
```

4. **Test Webhook Endpoint**:
```powershell
# Use Stripe CLI to trigger test webhook
stripe trigger checkout.session.completed
```

5. **Monitor Webhook Events**:
```powershell
# Watch webhook events in real-time
stripe listen --forward-to https://jobmatch.zip/api/subscription/webhook
```

## Verification Checklist

- [x] Backend `.env` updated with `FRONTEND_URL=https://jobmatch.zip`
- [x] Frontend API route uses HTTPS for production
- [x] Stripe webhook endpoint created at `https://jobmatch.zip/api/subscription/webhook`
- [x] Webhook secret configured in backend `.env`
- [x] NGINX configured to proxy port 443 → internal ports
- [ ] Test checkout flow end-to-end
- [ ] Verify webhook events are received
- [ ] Test with Stripe test card: `4242 4242 4242 4242`

## CLI Testing Commands

### Check Webhook Status
```powershell
stripe webhook_endpoints list
```

### Trigger Test Events
```powershell
# Test successful checkout
stripe trigger checkout.session.completed

# Test subscription creation
stripe trigger customer.subscription.created

# Test payment success
stripe trigger invoice.payment_succeeded
```

### Monitor Logs
```powershell
# Backend logs
cd E:\JobFinder\backend
tail -f logs/api.log

# NGINX logs
tail -f /var/log/nginx/jobmatch_access.log
```

## Troubleshooting

### Issue: "Failed to create checkout session"
**Check**:
```powershell
# Verify backend is running
curl http://localhost:8000/health

# Check NGINX is proxying correctly
curl https://jobmatch.zip/health
```

### Issue: "Webhook signature verification failed"
**Fix**:
1. Verify webhook secret matches:
```powershell
stripe webhook_endpoints retrieve we_1SX0wsBObYs4DzR45k3wGTNy
```
2. Update backend `.env` if secret changed

### Issue: "Connection refused to port 8000"
**Cause**: Trying to access internal port directly from external network

**Fix**: Always use HTTPS on port 443:
- ❌ `http://jobmatch.zip:8000/api/`
- ✅ `https://jobmatch.zip/api/`

## Production Deployment

When ready for production (currently using test mode):

1. **Switch to Live Stripe Keys**:
```powershell
# Get live keys from Stripe Dashboard
# Update backend/.env:
STRIPE_SECRET_KEY=sk_live_...
```

2. **Create Live Webhook**:
```powershell
stripe webhook_endpoints create --live `
  -d "url=https://jobmatch.zip/api/subscription/webhook" `
  -d "enabled_events[0]=customer.subscription.created" `
  # ... (same events as test)
```

3. **Update Webhook Secret**:
```powershell
# Get new secret from live webhook
# Update backend/.env with live webhook secret
```

## Summary

✅ **Configuration Complete**
- All external traffic uses HTTPS on port 443
- Internal services communicate on ports 8000 (backend) and 3000 (frontend)
- NGINX handles SSL termination and proxying
- Stripe webhooks configured and ready
- No manual port specification needed in URLs

**Next Step**: Test the checkout flow using the CLI commands above.
