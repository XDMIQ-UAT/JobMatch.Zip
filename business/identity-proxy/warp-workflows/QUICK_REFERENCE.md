# Auth Flow Agent - Quick Reference

**Account**: zsbw@proton.me  
**Scope**: Account-level authentication (not personal identity)  
**Agent Type**: auth_flow_specialist

## Quick Commands

```bash
# Activate agent
pwsh scripts/activate-auth-flow-agent.ps1

# Check status
warp auth-status

# Test flows
warp auth-test-magic-link        # Test full magic link flow
warp auth-send-magic-link        # Send test magic link email
warp auth-test-simple            # Simple email delivery test

# Debug
warp auth-check-ses              # Check SES configuration
warp auth-test-endpoint          # Test authentication endpoint
warp auth-get-magic-link         # Get magic link for specific email
```

## Authentication Flows

### 1. OAuth Flow
```
User clicks login
  ↓
Redirect to provider (Facebook/Google/etc)
  ↓
Provider callback with auth code
  ↓
Exchange code for token
  ↓
Link to anonymous_id
  ↓
Create session
```

**Endpoints**: 
- `/api/social-auth/{provider}/login`
- `/api/social-auth/{provider}/callback`

**Code**: `backend/auth/social_auth.py`, `backend/api/social_auth.py`

### 2. Magic Link Flow
```
User enters email
  ↓
Generate secure token (30-min expiry)
  ↓
Send email via SES
  ↓
User clicks link
  ↓
Verify token (one-time use)
  ↓
Create session
```

**Endpoints**: 
- `/api/auth/magic-link/send`
- `/api/auth/magic-link/verify`

**Code**: `backend/auth/social_auth.py`, `backend/auth/email_provider.py`

### 3. Anonymous Session
```
User visits site
  ↓
Generate anonymous_id (UUID4)
  ↓
Store in database
  ↓
Return to client
```

**Endpoint**: `/api/auth/anonymous/create`

**Code**: `backend/auth/anonymous_identity.py`

## Common Issues

### OAuth Issues

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| Invalid redirect_uri | Callback fails | Check `SOCIAL_AUTH_REDIRECT_URI` env var |
| CSRF state mismatch | State validation fails | Check state storage (Redis/memory) |
| Token exchange failure | Can't get access token | Verify client_id/client_secret |

### Magic Link Issues

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| Email not delivered | User doesn't receive email | Run `warp auth-check-ses` |
| Token expired | Link shows expired | Check server time sync |
| Already used | Link clicked twice | Show "already used" message |

### Session Issues

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| Session not persisting | User logged out unexpectedly | Check cookie settings |
| ID collision | Duplicate anonymous_id | Check UUID generation |

## Debugging Workflow

```bash
# 1. Identify which flow is failing
#    Check logs: backend/logs/auth.log

# 2. Test the specific flow
warp auth-test-magic-link      # For magic link
# (OAuth test TBD)

# 3. Check configuration
warp auth-check-ses            # For email/SES
# Check .env for OAuth credentials

# 4. Review code references
#    backend/auth/social_auth.py
#    backend/api/social_auth.py
#    backend/auth/email_provider.py

# 5. Check docs
#    docs/MAGIC_LINK_AUTHENTICATION.md
#    docs/SES_PRODUCTION_ACCESS.md
```

## Environment Variables

### Required for Magic Link
```bash
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
SES_FROM_EMAIL=noreply@yourdomain.com
SES_VERIFIED_EMAILS=test@example.com  # For sandbox
```

### Required for OAuth
```bash
FACEBOOK_CLIENT_ID=xxx
FACEBOOK_CLIENT_SECRET=xxx
LINKEDIN_CLIENT_ID=xxx
LINKEDIN_CLIENT_SECRET=xxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
MICROSOFT_CLIENT_ID=xxx
MICROSOFT_CLIENT_SECRET=xxx
SOCIAL_AUTH_REDIRECT_URI=https://yourdomain.com/api/social-auth/callback
```

### Required for Sessions
```bash
SESSION_SECRET=xxx
SESSION_COOKIE_DOMAIN=.yourdomain.com
SESSION_COOKIE_SECURE=true
REDIS_URL=redis://localhost:6379
```

## File Structure

```
business/identity-proxy/warp-workflows/
├── auth-flow-agent.yaml      # Main agent config
├── README.md                  # Full integration guide
└── QUICK_REFERENCE.md         # This file

backend/
├── api/
│   ├── auth.py               # Auth API endpoints
│   └── social_auth.py        # Social auth API
└── auth/
    ├── anonymous_identity.py # Anonymous session management
    ├── email_provider.py     # Email/magic link provider
    ├── oauth_providers.py    # OAuth provider config
    ├── social_auth.py        # Social auth implementation
    └── sms_provider.py       # SMS/VoIP (future)

frontend/
└── app/
    └── auth/
        ├── page.tsx          # Auth UI
        └── magic-link/
            └── page.tsx      # Magic link UI

scripts/
├── activate-auth-flow-agent.ps1   # Activate agent
├── test-magic-link.ps1            # Test magic link
├── test-magic-link-send.ps1       # Send test email
├── get-magic-link.ps1             # Get link for email
├── test-email-auth-endpoint.ps1   # Test endpoint
├── test-email-simple.ps1          # Simple email test
└── check-ses-config.ps1           # Check SES config

docs/
├── MAGIC_LINK_AUTHENTICATION.md
├── MAGIC_LINK_SECURITY.md
├── SES_PRODUCTION_ACCESS.md
└── EMAIL_SPAM_FIX.md
```

## Agent Coordination

```
Auth Flow Agent (You Are Here)
    ↓
    ├─→ Identity Proxy Agent
    │   └─ Anonymous session management
    │
    ├─→ Security Agent
    │   └─ CSRF, rate limiting, breach detection
    │
    └─→ Pieces Agent
        └─ Knowledge sync, context preservation
```

## Key Principles

1. **Account-level only**: No personal identity data
2. **Anonymous-first**: Always maintain zero-knowledge
3. **Privacy-preserving**: Hash sensitive data, never sync PII
4. **Security-focused**: CSRF protection, rate limiting, one-time tokens
5. **Recoverable**: Support rollback if issues occur

## Testing Checklist

- [ ] OAuth flows complete successfully
- [ ] Magic links delivered and verified
- [ ] Sessions persist across requests
- [ ] Anonymous sessions work without auth
- [ ] HTTPS enforced in production
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Tokens expire appropriately
- [ ] One-time use enforced
- [ ] No PII in anonymous_id
- [ ] Identity stored separately

## Escalation

If you can't resolve an issue:

```bash
# Auto-escalate after 3 failed attempts
# Manual escalation:
warp escalate auth-issue --reason "description"
warp request-review auth-flow --context "context"
```

**Escalation triggers**:
- Cannot resolve after 3 attempts → Human review
- Potential security breach → Immediate escalation
- Breaking change needed → Human approval

## Support

1. Check this quick reference
2. Review `README.md` for details
3. Check `auth-flow-agent.yaml` for flows
4. Run diagnostics: `warp auth-check-ses`
5. Check logs: `backend/logs/auth.log`
6. Escalate if needed

---

**Last Updated**: 2025-11-22  
**Version**: 1.0  
**For**: Account zsbw@proton.me
