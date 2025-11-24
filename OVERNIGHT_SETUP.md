# JobMatch Overnight Setup Status

## ✅ Completed
- Stripe configured: $1/month pricing ready
  - Product: `prod_TTufp6ZDcEoeeC`
  - Price: `price_1SWwqbBObYs4DzR4HldYKqqe`
- Landing page updated to show $1/month
- GCP billing enabled on `futurelink-private-112912460`
- VM started: 136.115.106.188
- Basic backend running (REV001)

## ❌ Needs Completion

### 1. Deploy Updated Backend with Voice/Subscription
**Current:** Backend is missing voice and subscription API routes  
**Need:** Deploy `E:\JobFinder\backend\api\` to VM

**Quick Fix:**
```powershell
# Package the updated backend
cd E:\JobFinder
tar -czf backend-full.tar.gz backend/

# Upload to VM
gcloud compute scp backend-full.tar.gz jobmatch-vm:/tmp/ --zone=us-central1-a --project=futurelink-private-112912460

# SSH in and deploy
gcloud compute ssh jobmatch-vm --zone=us-central1-a --project=futurelink-private-112912460

# On VM:
sudo tar -xzf /tmp/backend-full.tar.gz -C /opt/jobmatch/jobmatch-ai/
cd /opt/jobmatch
sudo docker compose restart backend
```

### 2. Configure Twilio Webhook
**Phone:** (626) 995-9974  
**Webhook URL:** `http://136.115.106.188:8000/api/voice/incoming`

**Steps:**
1. Go to https://console.twilio.com/
2. Navigate to Phone Numbers → Active Numbers
3. Click on (626) 995-9974
4. Under "Voice Configuration":
   - A CALL COMES IN: Webhook
   - URL: `http://136.115.106.188:8000/api/voice/incoming`
   - HTTP: POST
5. Save

### 3. Test Everything
```powershell
# Test backend health
curl http://136.115.106.188:8000/health

# Test voice endpoint
curl http://136.115.106.188:8000/api/voice/health

# Test subscription endpoint
curl -X POST http://136.115.106.188:8000/api/subscription/create-checkout-session `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com"}'

# Test Twilio call
# Call (626) 995-9974 from your phone
```

## Voice Menu Structure (Editable)

Located in: `E:\JobFinder\backend\api\voice.py`

**Current Menu:**
- Press 1: Learn about services
- Press 2: Speak with AI assistant  
- Press 3: Schedule callback
- Press 9: End call

**To Edit Voice Tree:**
1. Edit `E:\JobFinder\backend\api\voice.py`
2. Modify the `handle_incoming_call()` and `handle_menu_selection()` functions
3. Redeploy backend

**Example Voice Tree Edit:**
```python
# In handle_incoming_call() - line 68-74
message = (
    "Welcome to Job Match. "
    "Press 1 for pricing information. "
    "Press 2 to start your job search. "
    "Press 3 to speak with support."
)
```

## Subscription Flow

**Landing Page:** http://136.115.106.188:3000 (or https://jobmatch.zip when DNS configured)

**Flow:**
1. User enters email
2. Clicks "Subscribe Now"
3. Redirected to Stripe Checkout ($1/month)
4. After payment → `/subscription/success`
5. Email captured in Stripe Customer records

## Cost Breakdown

**Platform Costs:** ~$417/month ($5,000/year)
- VM hosting
- Domain
- Stripe fees (2.9% + $0.30)

**Break-Even:** 417 users × $1/month = $417/month

## Support Contact

**Public Line:** (626) 995-9974 (Twilio - AI voice tree)  
**Private Line:** (213) 248-4250 (Keep separate, don't publish)

## Next Session (Tomorrow)
- Explain FutureLink.zip project
- Optimize $16k/month costs
- Review overnight autonomous work results
