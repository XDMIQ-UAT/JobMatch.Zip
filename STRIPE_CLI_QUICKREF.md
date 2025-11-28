# Stripe CLI Quick Reference - Port 443 Only

## Configuration Summary
✅ External: `https://jobmatch.zip` (port 443 only)  
✅ Internal: Backend on 8000, Frontend on 3000  
✅ Webhook: `https://jobmatch.zip/api/subscription/webhook`

## Essential Commands

### View Webhook Configuration
```powershell
stripe webhook_endpoints list
stripe webhook_endpoints retrieve we_1SX0wsBObYs4DzR45k3wGTNy
```

### Test Checkout Flow
```powershell
# Create a test checkout session
curl -X POST https://jobmatch.zip/api/subscription/create-checkout-session `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com"}'
```

### Trigger Test Events
```powershell
# Test checkout completion
stripe trigger checkout.session.completed

# Test subscription lifecycle
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted

# Test payment events
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

### Listen to Webhook Events (Real-time)
```powershell
# Forward webhooks to local testing
stripe listen --forward-to https://jobmatch.zip/api/subscription/webhook

# Or to local backend for debugging
stripe listen --forward-to http://localhost:8000/api/subscription/webhook
```

### View Event Logs
```powershell
# List recent events
stripe events list --limit 10

# Get specific event details
stripe events retrieve evt_xxxxx
```

### Customer Management
```powershell
# List customers
stripe customers list --limit 5

# Get customer details
stripe customers retrieve cus_xxxxx

# List customer subscriptions
stripe subscriptions list --customer cus_xxxxx
```

## Testing Workflow

### 1. Quick Health Check
```powershell
# Test backend is accessible via NGINX on 443
curl https://jobmatch.zip/health

# Test API endpoint
curl https://jobmatch.zip/api/v1
```

### 2. Create Test Subscription
```powershell
# Step 1: Create checkout session
$response = curl -X POST https://jobmatch.zip/api/subscription/create-checkout-session `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com"}' | ConvertFrom-Json

# Step 2: Note the checkout URL
Write-Host "Checkout URL: $($response.url)"

# Step 3: Use test card 4242 4242 4242 4242 to complete checkout
```

### 3. Monitor Webhooks
```powershell
# In separate terminal, listen for events
stripe listen --forward-to https://jobmatch.zip/api/subscription/webhook

# Trigger test event
stripe trigger checkout.session.completed

# Check webhook was received
stripe events list --limit 1
```

## Test Cards

| Card Number | Scenario |
|------------|----------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Decline |
| 4000 0025 0000 3155 | Requires authentication |

- Expiry: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits

## Troubleshooting Commands

### Check Configuration
```powershell
# Verify .env settings
cd E:\JobFinder\backend
Get-Content .env | Select-String -Pattern "STRIPE|FRONTEND"
```

### Test Internal Ports
```powershell
# Backend (should work on localhost only)
curl http://localhost:8000/health

# Frontend (should work on localhost only)
curl http://localhost:3000
```

### Test External Access (Port 443 Only)
```powershell
# ✅ Correct - uses port 443
curl https://jobmatch.zip/api/subscription/webhook

# ❌ Wrong - don't expose internal ports
# curl http://jobmatch.zip:8000/api/
```

## Common Issues & Fixes

### Issue: "Webhook signature failed"
```powershell
# Get current webhook secret
stripe webhook_endpoints retrieve we_1SX0wsBObYs4DzR45k3wGTNy | jq -r .secret

# Update .env if needed
cd E:\JobFinder\backend
# Edit .env: STRIPE_WEBHOOK_SECRET=whsec_...
```

### Issue: "Cannot connect to checkout session"
```powershell
# Check NGINX is running and proxying
curl -I https://jobmatch.zip/health

# Check backend is running
curl http://localhost:8000/health
```

### Issue: "CORS error"
```powershell
# Verify FRONTEND_URL in backend .env
cd E:\JobFinder\backend
Get-Content .env | Select-String "FRONTEND_URL"
# Should be: FRONTEND_URL=https://jobmatch.zip
```

## Production Switch

When ready for production (currently test mode):

```powershell
# 1. Create live webhook endpoint
stripe webhook_endpoints create --live `
  -d "url=https://jobmatch.zip/api/subscription/webhook" `
  -d "enabled_events[0]=checkout.session.completed" `
  # ... (add all 6 events)

# 2. Update backend/.env with live keys
# STRIPE_SECRET_KEY=sk_live_...
# STRIPE_WEBHOOK_SECRET=whsec_live_...

# 3. Test with real card
curl -X POST https://jobmatch.zip/api/subscription/create-checkout-session `
  -H "Content-Type: application/json" `
  -d '{"email":"real@customer.com"}'
```

---

**Configuration Location**: `E:\JobFinder\STRIPE_443_CONFIG.md`  
**Webhook ID**: `we_1SX0wsBObYs4DzR45k3wGTNy`  
**Status**: ✅ Ready for testing
