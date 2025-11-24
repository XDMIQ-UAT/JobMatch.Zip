# Stripe Payment Integration Setup

This guide will help you set up real Stripe payments for JobMatch.zip.

## Prerequisites

1. A Stripe account (sign up at https://stripe.com)
2. Access to your Stripe Dashboard
3. A domain for webhooks (jobmatch.zip)

## Step 1: Get Your Stripe API Keys

### For Testing (Development)
1. Log into your Stripe Dashboard: https://dashboard.stripe.com
2. Navigate to **Developers** → **API keys**
3. Copy your **Publishable key** (starts with `pk_test_`)
4. Copy your **Secret key** (starts with `sk_test_`)

### For Production (Live Payments)
1. In Stripe Dashboard, toggle to **Live mode** (top right)
2. Navigate to **Developers** → **API keys**
3. Copy your **Live Publishable key** (starts with `pk_live_`)
4. Copy your **Live Secret key** (starts with `sk_live_`)

## Step 2: Configure Environment Variables

### Backend Configuration
Add to `E:\JobFinder\backend\.env`:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
FRONTEND_URL=https://jobmatch.zip
```

### Frontend Configuration  
Add to `E:\JobFinder\frontend\.env.local`:

```env
# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLISHABLE_KEY_HERE
```

## Step 3: Set Up Stripe Webhooks

Webhooks allow Stripe to notify your backend about payment events.

1. Go to **Developers** → **Webhooks** in Stripe Dashboard
2. Click **Add endpoint**
3. Enter your webhook URL: `https://jobmatch.zip/api/subscription/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**
6. Copy the **Signing secret** (starts with `whsec_`)
7. Add it to your backend `.env` file as `STRIPE_WEBHOOK_SECRET`

## Step 4: Test the Integration

### Using Stripe Test Mode

Before going live, test with Stripe's test cards:

**Successful payment:**
- Card number: `4242 4242 4242 4242`
- Expiry: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits

**Declined payment:**
- Card number: `4000 0000 0000 0002`

**Requires authentication:**
- Card number: `4000 0025 0000 3155`

### Testing the Flow

1. Start your backend: `cd E:\JobFinder\backend && python main.py`
2. Start your frontend: `cd E:\JobFinder\frontend && npm run dev`
3. Visit: http://localhost:3000/landing
4. Enter your email and click "Subscribe Now"
5. Use test card `4242 4242 4242 4242` to complete payment
6. Check your backend logs for webhook events

## Step 5: Go Live

### Important Checklist

- [ ] Switch to **Live mode** in Stripe Dashboard
- [ ] Update all API keys to production keys (`pk_live_` and `sk_live_`)
- [ ] Configure webhook endpoint for production domain
- [ ] Test with a real card (your own)
- [ ] Verify webhook events are received
- [ ] Set up proper error logging
- [ ] Configure email notifications for failed payments

### Production Deployment

1. Update environment variables on your production server
2. Deploy updated code
3. Test subscription flow with real payment
4. Monitor Stripe Dashboard for any issues

## Subscription Configuration

Current settings (modify in `backend/api/subscription.py`):

```python
WEEKLY_PRICE = 4790  # $47.90 in cents
MAX_RESUBSCRIPTIONS = 6
REFUND_PERIOD_DAYS = 14
CREDIT_PERIOD_DAYS = 60
```

## Refund & Credit Policy Implementation

### Automatic Refunds (0-14 days)
- Users can request refunds within 14 days
- Processed automatically via the `/api/subscription/request-refund` endpoint
- Subscription is cancelled immediately

### Credits (15-60 days)
- After 14 days, users must request credits
- Requires written correspondence (manual review)
- Use `/api/subscription/request-credits` endpoint
- Support team reviews and approves/denies

### After 60 Days
- No refunds or credits available
- Standard subscription terms apply

## API Endpoints

### Create Checkout Session
```
POST /api/subscription/create-checkout-session
Body: { "email": "user@example.com", "user_id": "optional_user_id" }
Response: { "session_id": "...", "url": "https://checkout.stripe.com/..." }
```

### Check Subscription Status
```
GET /api/subscription/status/{customer_id}
Response: { "has_active_subscription": true, "subscription_count": 1, ... }
```

### Cancel Subscription
```
POST /api/subscription/cancel
Body: { "subscription_id": "sub_..." }
Response: { "success": true, "message": "..." }
```

### Request Refund
```
POST /api/subscription/request-refund
Body: { "subscription_id": "sub_...", "reason": "optional reason" }
Response: { "success": true, "refund": {...} }
```

### Request Credits
```
POST /api/subscription/request-credits
Body: { "subscription_id": "sub_...", "reason": "required", "email": "user@example.com" }
Response: { "success": true, "message": "..." }
```

## Stripe Dashboard Features

### Monitor Subscriptions
- View all active subscriptions
- See upcoming billing dates
- Track MRR (Monthly Recurring Revenue)

### Handle Customer Issues
- Refund payments manually
- Cancel subscriptions
- Update payment methods
- View payment history

### Analytics
- Revenue tracking
- Customer lifetime value
- Churn rates
- Failed payment analysis

## Security Best Practices

1. **Never expose secret keys** in frontend code
2. **Always verify webhook signatures** before processing events
3. **Use HTTPS** for all production endpoints
4. **Store API keys securely** in environment variables
5. **Monitor for suspicious activity** in Stripe Dashboard
6. **Set up fraud detection** rules in Stripe
7. **Enable 3D Secure** for additional security

## Troubleshooting

### Webhook not receiving events
- Check webhook URL is publicly accessible
- Verify webhook secret matches Stripe Dashboard
- Check server logs for errors
- Test webhook endpoint with Stripe CLI

### Payments failing
- Check if using correct API keys (test vs live)
- Verify customer has valid payment method
- Check for insufficient funds
- Review Stripe logs for detailed error messages

### Subscription not activating
- Verify webhook events are being processed
- Check database for subscription record
- Review application logs for errors
- Confirm checkout session completed successfully

## Support Resources

- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com
- Stripe Status: https://status.stripe.com
- JobMatch Support: support@jobmatch.zip

## Next Steps

After completing this setup:

1. Test the complete subscription flow
2. Configure email notifications for subscription events
3. Set up proper error monitoring and alerting
4. Create a customer support workflow for refund/credit requests
5. Monitor Stripe Dashboard regularly for issues
6. Set up automated receipts via email

---

**Note:** This is a production-ready integration. Always test thoroughly in Stripe's test mode before switching to live mode. Real money will be charged when using live API keys!
