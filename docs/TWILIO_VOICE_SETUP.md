# Twilio Voice Integration - JobMatch.zip

## Overview
JobMatch now has Twilio-compatible voice endpoints that handle incoming phone calls with an interactive voice menu.

## Endpoints

### Primary Voice Webhook
```
URL: https://jobmatch.zip/api/voice/incoming
Method: POST (Twilio default) or GET
```

### Menu Selection Handler
```
URL: https://jobmatch.zip/api/voice/menu
Method: POST
```

### Call Status Callback (Optional)
```
URL: https://jobmatch.zip/api/voice/status
Method: POST
```

### Health Check
```
URL: https://jobmatch.zip/api/voice/health
Method: GET
```

## Twilio Console Setup

### 1. Purchase a Phone Number
1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Phone Numbers** → **Buy a Number**
3. Select a number with **Voice** capabilities
4. Purchase the number

### 2. Configure Voice Webhook
1. In Twilio Console, go to **Phone Numbers** → **Manage** → **Active Numbers**
2. Click on your purchased number
3. Scroll to **Voice Configuration**
4. Set:
   - **A CALL COMES IN**: Webhook
   - **URL**: `https://jobmatch.zip/api/voice/incoming`
   - **HTTP Method**: POST
   - **Fallback URL** (optional): `https://jobmatch.zip/api/voice/incoming`
5. Click **Save**

### 3. Configure Status Callback (Optional)
1. In the same phone number configuration
2. Scroll to **Call Status Changes**
3. Set:
   - **URL**: `https://jobmatch.zip/api/voice/status`
   - **HTTP Method**: POST
   - **Events**: Select "Completed" and "No Answer"
4. Click **Save**

## Call Flow

When someone calls your Twilio number:

1. **Welcome Message** (auto-played):
   ```
   "Welcome to Job Match dot zip, the AI-powered job matching 
   platform for LLC owners. Press 1 to learn about our services. 
   Press 2 to speak with our AI assistant. Press 3 to schedule 
   a callback. Press 9 to end this call."
   ```

2. **Caller Presses 1** - About Services:
   ```
   "Job Match helps LLC owners find perfect job matches using AI. 
   We analyze your skills, experience, and goals to match you with 
   opportunities. Visit jobmatch dot zip to get started. Goodbye!"
   ```

3. **Caller Presses 2** - AI Assistant:
   ```
   "Our AI assistant is available on our website at jobmatch dot zip. 
   You can chat with our intelligent matching system 24/7. 
   Visit us online to get started. Goodbye!"
   ```

4. **Caller Presses 3** - Schedule Callback:
   ```
   "To schedule a callback, please visit jobmatch dot zip and fill 
   out our contact form. Our team will reach out within 24 hours. 
   Goodbye!"
   ```

5. **Caller Presses 9** - End Call:
   ```
   "Thank you for calling Job Match. Goodbye!"
   ```

## Testing

### Test Locally (ngrok)
```bash
# Start ngrok tunnel
ngrok http 8000

# Update Twilio webhook URL to:
https://YOUR-NGROK-URL.ngrok.io/api/voice/incoming

# Call your Twilio number to test
```

### Test Endpoint Directly
```bash
# Health check
curl https://jobmatch.zip/api/voice/health

# Test incoming call (simulated)
curl -X POST https://jobmatch.zip/api/voice/incoming \
  -d "From=+1234567890" \
  -d "To=+0987654321" \
  -d "CallSid=CA1234567890" \
  -d "CallStatus=ringing"
```

## Required SSL/TLS
⚠️ **Important**: Twilio requires HTTPS endpoints. Make sure:
- jobmatch.zip has a valid SSL certificate
- Certificate is not self-signed
- Server supports TLS 1.2 or higher

## Monitoring & Logs

All voice interactions are logged with:
- Caller phone number (From)
- Called number (To)
- Unique Call SID
- Menu selections
- Call status and duration

Check backend logs:
```bash
# In production
tail -f /var/log/jobmatch/backend.log

# In Docker
docker logs jobmatch-backend -f
```

## Customization

### Change Voice
Edit `backend/api/voice.py`:
```python
# Current: Polly.Joanna (US female)
# Options: Polly.Matthew (US male), Polly.Amy (UK female), 
#          Polly.Brian (UK male), alice, man, woman
<Say voice="Polly.Matthew">Your message</Say>
```

### Add More Menu Options
Add to `handle_menu_selection()`:
```python
elif Digits == "4":
    message = "Your new menu option message"
```

### Forward to Real Person
Replace TwiML with:
```python
twiml = '<Response><Dial>+1234567890</Dial></Response>'
```

## Security

- All endpoints are protected by FastAPI middleware
- Rate limiting: 60 requests/minute per IP
- CORS restrictions apply
- Twilio request validation can be added:

```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
is_valid = validator.validate(url, post_data, signature)
```

## Deployment

The voice endpoints are automatically deployed with the backend service. No additional deployment needed.

```bash
# Restart backend to apply changes
docker-compose restart backend
```

## Troubleshooting

### Twilio Returns 11200 Error
- Endpoint is unreachable
- Check SSL certificate
- Verify URL is publicly accessible

### No Audio Playing
- Check TwiML syntax
- Verify `<Say>` tags are properly formatted
- Test with Twilio's TwiML bin first

### Menu Not Working
- Ensure `<Gather>` action URL is absolute or relative to domain
- Check `numDigits` matches expected input
- Increase timeout if needed

## Cost Estimate

Twilio pricing (as of 2024):
- Phone number: ~$1-2/month
- Incoming calls: $0.0085/minute (US)
- Voice minutes: Varies by region

Estimate: ~$10-20/month for light usage

## Next Steps

1. ✅ Voice endpoint created
2. ⬜ Purchase Twilio number
3. ⬜ Configure webhook in Twilio Console
4. ⬜ Test with real phone call
5. ⬜ Add call logging to database (optional)
6. ⬜ Set up call analytics (optional)
7. ⬜ Add Twilio request signature validation (optional)
