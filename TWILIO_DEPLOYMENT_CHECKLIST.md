# Twilio Voice Deployment Checklist

## ✅ Code Complete
- [x] Voice API endpoint created (`backend/api/voice.py`)
- [x] Integrated into FastAPI app (`backend/main.py`)
- [x] Test suite created (`test_voice_endpoint.py`)
- [x] Documentation created (`docs/TWILIO_VOICE_SETUP.md`)
- [x] Changes committed to git

## 📋 Deployment Steps

### 1. Local Testing
```bash
# Start the backend
cd E:\JobFinder
docker-compose up backend

# Run tests (in another terminal)
python test_voice_endpoint.py
```

### 2. Deploy to Production
```bash
# Push changes to repository
git push origin master

# SSH to production server
ssh user@jobmatch.zip

# Pull latest changes
cd /path/to/jobmatch
git pull

# Restart backend
docker-compose restart backend

# Verify deployment
curl https://jobmatch.zip/api/voice/health
```

### 3. Configure Twilio
1. **Go to Twilio Console**: https://console.twilio.com/
2. **Buy a Phone Number**:
   - Navigate: Phone Numbers → Buy a Number
   - Select number with Voice capability
   - Purchase

3. **Configure Webhook**:
   - Navigate: Phone Numbers → Manage → Active Numbers
   - Click your number
   - Under "Voice Configuration":
     - **A CALL COMES IN**: Webhook
     - **URL**: `https://jobmatch.zip/api/voice/incoming`
     - **HTTP**: POST
   - Click Save

4. **Optional - Status Callback**:
   - Under "Call Status Changes":
     - **URL**: `https://jobmatch.zip/api/voice/status`
     - **HTTP**: POST
     - Events: Completed, No Answer
   - Click Save

### 4. Test with Real Call
```bash
# Call your Twilio number from your phone
# Expected flow:
# 1. Hear welcome message
# 2. Press 1, 2, 3, or 9
# 3. Hear appropriate response
# 4. Call ends

# Check logs
docker logs jobmatch-backend -f | grep "Incoming call"
```

### 5. Verify Endpoints
```bash
# Health check
curl https://jobmatch.zip/api/voice/health

# Test incoming webhook (simulated)
curl -X POST https://jobmatch.zip/api/voice/incoming \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "CallSid=TEST123" \
  -d "CallStatus=ringing"
```

## 🔒 Security Checklist
- [ ] SSL certificate valid on jobmatch.zip
- [ ] Rate limiting configured (60 req/min)
- [ ] CORS properly configured
- [ ] Logs sanitize phone numbers (optional)
- [ ] Consider adding Twilio signature validation (optional)

## 📊 Monitoring
- [ ] Set up call logging to database (optional)
- [ ] Configure alerts for failed calls
- [ ] Monitor call duration/costs in Twilio Console
- [ ] Review logs weekly:
  ```bash
  docker logs jobmatch-backend | grep "voice"
  ```

## 💰 Cost Tracking
- Phone number: ~$1-2/month
- Incoming calls: ~$0.0085/minute
- Set up billing alerts in Twilio Console

## 🎯 Next Steps (Optional)
- [ ] Add database logging for calls
- [ ] Implement Twilio signature validation
- [ ] Add more menu options
- [ ] Integrate with CRM/contact form
- [ ] Add voicemail capability
- [ ] Forward to real person option
- [ ] Multi-language support

## 📞 Current Menu Structure
```
Main Menu:
├─ 1: About Services
├─ 2: AI Assistant Info
├─ 3: Schedule Callback
└─ 9: End Call
```

## 🐛 Troubleshooting

### "Twilio returned 11200"
- Check SSL certificate
- Verify URL is publicly accessible
- Test with: `curl -I https://jobmatch.zip/api/voice/incoming`

### "No audio playing"
- Check TwiML syntax in logs
- Test TwiML at: https://www.twilio.com/labs/twiml-generator

### "Menu not responding"
- Increase `timeout` in `<Gather>` tag
- Check logs for digit received
- Verify POST to /api/voice/menu succeeds

## 📝 Notes
- Endpoints support both GET and POST (Twilio uses POST)
- TwiML uses Amazon Polly voice "Joanna" by default
- All calls are logged with CallSid for tracking
- No PII stored unless explicitly added

---

**Ready to deploy?** Run the local tests first, then follow steps 2-4 above.

For questions, see: `docs/TWILIO_VOICE_SETUP.md`
