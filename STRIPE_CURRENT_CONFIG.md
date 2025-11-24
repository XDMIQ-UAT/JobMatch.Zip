# Current Stripe Configuration

## ✅ Configured via Stripe CLI

### Product Details
- **Product ID:** `prod_TTuCRmeLllUuPa`
- **Name:** JobMatch AI - 2 Seat License
- **Description:** AI-powered job matching service with 2 user seats
- **Type:** Service
- **Status:** Active (Test Mode)

### Pricing Details
- **Price ID:** `price_1SWwOTBObYs4DzR4kKQZPQ2j`
- **Amount:** $115.00 USD per week
- **Currency:** USD
- **Billing:** Weekly recurring
- **Trial Period:** 7 days (free trial before first charge)
- **Seats:** 2 user seats included
- **Status:** Active (Test Mode)

## Current Subscription Features

### What's Included
✅ 2 user seats per subscription
✅ 7-day free trial (no charge until trial ends)
✅ Weekly billing at $115/week after trial
✅ AI-powered job matching
✅ Direct messaging with hiring managers
✅ Real-time application tracking
✅ Interview preparation & coaching
✅ Career insights & salary analytics

### Policies
- **Free Trial:** 7 days - try risk-free, no charge until trial ends
- **Refund Policy:** Full refund within 14 days of first payment
- **Credits:** Available within 60 days with written correspondence
- **Max Resubscriptions:** 6 total subscriptions allowed per customer
- **Cancellation:** Cancel anytime, no questions asked

## Integration Status

### Backend (Python/FastAPI)
- ✅ File: `E:\JobFinder\backend\api\subscription.py`
- ✅ Routes configured:
  - `POST /api/subscription/create-checkout-session`
  - `GET /api/subscription/status/{customer_id}`
  - `POST /api/subscription/cancel`
  - `POST /api/subscription/request-refund`
  - `POST /api/subscription/request-credits`
  - `POST /api/subscription/webhook`
- ✅ Pricing: $115/week (11500 cents)
- ✅ Trial: 7 days
- ✅ Product ID & Price ID hardcoded
- ✅ Stripe SDK added to requirements.txt

### Frontend (Next.js)
- ✅ File: `E:\JobFinder\frontend\app\landing\page.tsx`
- ✅ Landing page displays:
  - $115/week pricing
  - 2 seats included badge
  - 7-day free trial notice
  - Feature list
  - Email subscription form
  - Ecosystem footer links
- ✅ Checkout integration ready

## Testing

### Test with Stripe CLI
```powershell
# View products
stripe products list

# View prices
stripe prices list

# Test webhook locally
stripe listen --forward-to http://localhost:8000/api/subscription/webhook
```

### Test Cards (Stripe Test Mode)
- **Successful:** `4242 4242 4242 4242`
- **Declined:** `4000 0000 0000 0002`
- **Requires Auth:** `4000 0025 0000 3155`

## Environment Variables Required

### Backend (.env)
```env
STRIPE_SECRET_KEY=sk_test_YOUR_KEY  # Get from Stripe Dashboard
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET  # Get from webhook setup
FRONTEND_URL=http://localhost:3000  # Or https://jobmatch.zip
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
```

## Next Steps to Go Live

1. **Get API Keys:**
   - Login to https://dashboard.stripe.com
   - Copy test keys for testing
   - When ready, switch to live mode and get live keys

2. **Install Dependencies:**
   ```powershell
   cd E:\JobFinder\backend
   pip install stripe==7.8.0
   ```

3. **Test Locally:**
   ```powershell
   # Terminal 1: Backend
   cd E:\JobFinder\backend
   python main.py

   # Terminal 2: Frontend
   cd E:\JobFinder\frontend
   npm run dev

   # Visit: http://localhost:3000/landing
   ```

4. **Set up Webhooks:**
   - Go to Stripe Dashboard → Developers → Webhooks
   - Add endpoint: `https://jobmatch.zip/api/subscription/webhook`
   - Select all subscription-related events
   - Copy webhook secret to .env

5. **Go Live:**
   - Switch to live mode in Stripe
   - Update all keys to live keys (pk_live_, sk_live_)
   - Test with real card
   - Monitor for issues

## Pricing Calculation

- **Per Seat Cost:** $57.50/week per user
- **Total (2 seats):** $115/week
- **Monthly Equivalent:** ~$498/month (4.33 weeks)
- **Annual Equivalent:** ~$5,980/year (52 weeks)

## Trial Period Details

- **Duration:** 7 days
- **Charge:** $0 during trial
- **First Payment:** Occurs on day 8 (after trial ends)
- **Access:** Full access during trial period
- **Cancellation:** Can cancel anytime during trial, no charge
- **Conversion:** Automatically converts to paid after trial

## Stripe Dashboard Access

- **Test Mode:** https://dashboard.stripe.com/test/dashboard
- **Live Mode:** https://dashboard.stripe.com/dashboard
- **Products:** https://dashboard.stripe.com/test/products
- **Subscriptions:** https://dashboard.stripe.com/test/subscriptions
- **Customers:** https://dashboard.stripe.com/test/customers
- **Webhooks:** https://dashboard.stripe.com/test/webhooks

---

**Configuration Date:** November 24, 2025  
**Stripe CLI Version:** 1.32.0  
**Mode:** Test (Ready for Production)
