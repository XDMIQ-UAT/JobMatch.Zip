# Quick Deployment Guide - Critical Fixes

**Target**: Complete remediation and prepare for go-live  
**Timeline**: Next 8 hours

---

## Prerequisites Checklist

- [ ] SSH access to jobmatch.zip production VM
- [ ] Git repository up to date locally
- [ ] Backend and frontend code ready to deploy
- [ ] AWS SES and Twilio credentials verified

---

## Step 1: Set SECRET_KEY on Production (15 minutes)

### Commands:
```bash
# SSH to production
ssh root@jobmatch.zip

# Navigate to backend directory
cd /opt/jobmatch/backend

# Backup current .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Add SECRET_KEY (replace with your generated key)
cat >> .env << 'EOF'
SECRET_KEY=120N8cGzpyMlxgP4-pt__eCKzJ3VnnEGeeZ_bsUNghw
ENVIRONMENT=production
EOF

# Verify environment file
grep -E "(SECRET_KEY|ENVIRONMENT)" .env

# Restart backend
sudo systemctl restart jobmatch-backend

# Check status
sudo systemctl status jobmatch-backend

# Verify health
curl -s https://jobmatch.zip/health | jq
```

### Expected Output:
```json
{
  "status": "healthy",
  "service": "backend",
  "version": "REV001",
  "release": "REV001"
}
```

### Verification:
- [ ] Backend starts without SECRET_KEY error
- [ ] Health endpoint responds
- [ ] Logs show no errors: `sudo journalctl -u jobmatch-backend -n 50`

---

## Step 2: Deploy Updated Backend Code (30 minutes)

### From Local Machine:

```powershell
# Navigate to project
cd E:\zip-jobmatch

# Verify changes
git status

# Stage critical files
git add backend/main.py
git add backend/api/age_verification.py
git commit -m "Add age verification and CORS fixes"

# Push to repository
git push origin main
```

### On Production VM:

```bash
# SSH to production
ssh root@jobmatch.zip

# Navigate to deployment directory
cd /opt/jobmatch

# Backup current code
tar -czf backup-$(date +%Y%m%d_%H%M%S).tar.gz backend/

# Pull latest changes
git pull origin main

# Verify files updated
ls -la backend/api/age_verification.py
grep "age_verification" backend/main.py

# Restart backend
sudo systemctl restart jobmatch-backend

# Monitor logs for errors
sudo journalctl -u jobmatch-backend -f
```

Press `Ctrl+C` after verifying no errors.

### Test Age Verification Endpoint:

```bash
# Test health check
curl -s https://jobmatch.zip/api/age-verification/health | jq

# Expected:
# {
#   "service": "age-verification",
#   "status": "operational",
#   "required_age": 18,
#   "compliance": "COPPA"
# }

# Test age verification (18+ - should pass)
curl -X POST https://jobmatch.zip/api/age-verification/verify \
  -H "Content-Type: application/json" \
  -d '{"birth_year": 1990, "birth_month": 1, "birth_day": 1}' | jq

# Expected:
# {
#   "is_verified": true,
#   "age": 35,
#   "required_age": 18,
#   "message": "Age verified: You are 35 years old"
# }

# Test under-18 (should fail)
curl -X POST https://jobmatch.zip/api/age-verification/verify \
  -H "Content-Type: application/json" \
  -d '{"birth_year": 2015, "birth_month": 1, "birth_day": 1}' | jq

# Expected:
# {
#   "is_verified": false,
#   "age": 10,
#   "required_age": 18,
#   "message": "Access denied: You must be at least 18 years old..."
# }
```

### Verification:
- [ ] Age verification endpoint responds
- [ ] 18+ users pass verification
- [ ] Under-18 users blocked
- [ ] No birthdate stored in database or logs

---

## Step 3: Test Security Headers (10 minutes)

```bash
# Test security headers from production
curl -I https://jobmatch.zip | grep -E "(Strict-Transport|X-Content-Type|X-Frame|Content-Security|Permissions)"
```

### Expected Headers:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; ...
Permissions-Policy: geolocation=(), microphone=(), ...
```

### Verification:
- [ ] All security headers present
- [ ] HSTS configured with max-age
- [ ] CSP properly configured

---

## Step 4: Test CORS Configuration (10 minutes)

```bash
# Test CORS preflight from allowed origin
curl -X OPTIONS https://jobmatch.zip/api/age-verification/verify \
  -H "Origin: https://jobmatch.zip" \
  -H "Access-Control-Request-Method: POST" \
  -v 2>&1 | grep -i "access-control"

# Should see:
# Access-Control-Allow-Origin: https://jobmatch.zip
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
# Access-Control-Allow-Headers: content-type, authorization, ...
```

### Test Restricted Methods:
```bash
# Try disallowed method (should fail)
curl -X TRACE https://jobmatch.zip/health -v 2>&1 | grep -i "405\|not allowed"
```

### Verification:
- [ ] Allowed origins work
- [ ] Specific methods enforced
- [ ] Wildcard (*) not present
- [ ] Disallowed methods rejected

---

## Step 5: Deploy Frontend (Optional - if integrating modal)

### If deploying age modal to frontend:

```bash
# From local machine
cd E:\zip-jobmatch\frontend

# Build production
npm run build

# Deploy to production (adjust path as needed)
scp -r out/* root@jobmatch.zip:/var/www/jobmatch/

# Or use deployment script if available
powershell scripts/deploy-frontend.ps1
```

### Add to Signup Flow:

Edit your signup page (e.g., `frontend/app/signup/page.tsx`):

```typescript
import { AgeVerificationModal } from '@/components/AgeVerificationModal';
import { useState } from 'react';

export default function SignupPage() {
  const [ageVerified, setAgeVerified] = useState(false);
  const [showAgeModal, setShowAgeModal] = useState(true);

  return (
    <>
      <AgeVerificationModal
        isOpen={showAgeModal && !ageVerified}
        onVerified={() => {
          setAgeVerified(true);
          setShowAgeModal(false);
        }}
      />
      
      {ageVerified && (
        <div>
          {/* Your signup form here */}
        </div>
      )}
    </>
  );
}
```

---

## Step 6: Test Authentication Endpoints (2 hours)

### Test Magic Link Endpoints:

```bash
# Check if endpoints exist
curl -s https://jobmatch.zip/api/docs | jq '.paths' | grep -i "magic\|auth"

# If endpoints exist, test send
curl -X POST https://jobmatch.zip/api/auth/magic-link/send \
  -H "Content-Type: application/json" \
  -d '{"email": "your-test-email@example.com"}' \
  -v
```

### If Endpoints Missing:
- Check if `backend/api/auth.py` and `backend/api/social_auth.py` exist
- Verify they're imported in `backend/main.py`
- Add if missing: `app.include_router(auth.router)`

### Check Backend Logs:

```bash
ssh root@jobmatch.zip
sudo journalctl -u jobmatch-backend -f

# Look for:
# - Email send attempts
# - AWS SES responses
# - Any errors in auth flow
```

### Verification:
- [ ] Magic link endpoint exists
- [ ] Email sends via AWS SES
- [ ] No PII in logs (emails redacted)
- [ ] Rate limiting works

---

## Step 7: Final Verification Checklist

### Security:
- [ ] SECRET_KEY set and not default
- [ ] PII redacted in logs
- [ ] Security headers present
- [ ] CORS restricted
- [ ] Rate limiting functional

### Compliance:
- [ ] Age verification endpoint working
- [ ] Under-18 users blocked
- [ ] No birthdate persistence
- [ ] GDPR deletion endpoint exists
- [ ] Privacy policy updated

### Operations:
- [ ] Backend healthy
- [ ] Frontend accessible
- [ ] Database connected
- [ ] Redis operational
- [ ] Monitoring alerts configured

---

## Rollback Procedure (If Issues Arise)

```bash
# SSH to production
ssh root@jobmatch.zip

# Stop backend
sudo systemctl stop jobmatch-backend

# Restore backup
cd /opt/jobmatch
tar -xzf backup-YYYYMMDD_HHMMSS.tar.gz

# Restart backend
sudo systemctl start jobmatch-backend

# Verify
curl https://jobmatch.zip/health
```

---

## Post-Deployment Monitoring (First 24 Hours)

### Metrics to Watch:

```bash
# Check backend logs every hour
ssh root@jobmatch.zip
sudo journalctl -u jobmatch-backend --since "1 hour ago" | grep -i "error\|critical\|warning"

# Monitor age verification usage
sudo journalctl -u jobmatch-backend --since "1 hour ago" | grep "age verification"

# Check failed authentication attempts
sudo journalctl -u jobmatch-backend --since "1 hour ago" | grep "authentication failed"
```

### Key Metrics:
- Authentication success rate (target: >95%)
- Age verification rejections (monitor for unusual patterns)
- API error rate (target: <1%)
- Response time (target: <500ms p99)
- Security incidents (target: 0)

---

## Success Criteria

Before declaring go-live ready:

- ✅ All critical fixes deployed
- ✅ Security headers verified
- ✅ CORS restrictions working
- ✅ Age verification functional
- ✅ SECRET_KEY secured
- ✅ PII redaction confirmed
- ✅ Authentication flow tested
- ✅ Monitoring configured
- ✅ Rollback procedure tested
- ✅ Privacy policy updated

---

## Support Contacts

**Technical Issues**: Create GitHub issue with `urgent` label  
**Security Incidents**: Document immediately, review C-Level report  
**Compliance Questions**: Refer to `docs/PRIVACY_POLICY.md`

---

**Prepared**: November 24, 2025  
**Target Completion**: November 25, 2025  
**Go-Live Target**: November 27-28, 2025
