# Warp Auth Flow Agent - Integration Guide

## Overview
This directory contains the **Auth Flow Agent** for Warp, a specialized agent focused on authentication flow issues at the account level for `zsbw@proton.me`. This agent operates independently from personal identity flows and maintains the platform's zero-knowledge, anonymous-first architecture.

## Purpose
The Auth Flow Agent handles:
- OAuth authentication flows (Facebook, LinkedIn, Google, Microsoft, Apple)
- Magic link email authentication
- SMS/VoIP verification (future)
- Anonymous session management
- Account-level security and session persistence

## Key Files

### `auth-flow-agent.yaml`
Primary configuration file defining:
- **Authentication flows**: OAuth, magic links, SMS/VoIP, anonymous sessions
- **Issue catalog**: Common auth problems and debugging steps
- **Warp workflow**: Detection, diagnosis, resolution procedures
- **Pieces MCP integration**: Knowledge sharing across sessions
- **Testing & validation**: Checklists and test scripts

## Quick Start

### 1. Activate Auth Flow Agent in Warp
```bash
# Set Warp to monitor auth flows
warp agent activate auth-flow

# View auth flow status
warp agent status auth-flow
```

### 2. Test Authentication Flows
```powershell
# Test magic link flow
pwsh scripts/test-magic-link.ps1

# Test OAuth flow (when available)
warp run business/identity-proxy/warp-workflows/test-oauth.yaml

# Check SES configuration
pwsh scripts/check-ses-config.ps1
```

### 3. Monitor Authentication
```bash
# Monitor auth logs in real-time
warp monitor auth

# Or manually:
tail -f backend/logs/auth.log
```

### 4. Debug Authentication Issues
```bash
# Run auth diagnostics
warp run business/identity-proxy/warp-workflows/debug-auth.yaml

# Check OAuth configuration
warp run business/identity-proxy/warp-workflows/check-oauth-config.yaml
```

## Account-Level vs Personal-Level

**IMPORTANT**: This agent operates at the **account level**, not the personal level.

### Account Level (This Agent)
- OAuth provider configuration
- Magic link token generation/validation
- Session management
- Authentication endpoints
- Security policies (CSRF, rate limiting)
- No access to personal identity data

### Personal Level (Not This Agent)
- User's real identity
- Personal profile information
- Identity linking/unlinking
- User preferences beyond authentication

## Authentication Flows

### OAuth Flow
1. **Initiation**: User clicks social login → `/api/social-auth/{provider}/login`
2. **Redirect**: OAuth provider authorization page
3. **Callback**: Provider returns to `/api/social-auth/{provider}/callback`
4. **Account Linking**: Link provider account to `anonymous_id`
5. **Session Creation**: Create authenticated session

### Magic Link Flow
1. **Request**: User enters email → `/api/auth/magic-link/send`
2. **Generation**: Create secure token (30-min expiration)
3. **Delivery**: Send email via AWS SES
4. **Verification**: User clicks link → `/api/auth/magic-link/verify`
5. **Session Creation**: Create authenticated session

### Anonymous Session Flow
1. **Visit**: User visits site (no auth required)
2. **Generation**: Create cryptographically secure `anonymous_id`
3. **Storage**: Store session in database
4. **Return**: Return `anonymous_id` to client

## Common Issues & Solutions

### OAuth Issues

#### Invalid redirect_uri
```yaml
Symptoms: OAuth callback fails with redirect_uri mismatch
Debug:
  - Check provider console redirect_uri configuration
  - Verify SOCIAL_AUTH_REDIRECT_URI environment variable
  - Ensure HTTPS in production
Code: backend/auth/oauth_providers.py, frontend/app/auth/page.tsx
```

#### CSRF state validation failure
```yaml
Symptoms: State parameter mismatch error
Debug:
  - Check state storage (Redis/in-memory)
  - Verify state expiration time
  - Check for race conditions in concurrent requests
Code: backend/api/social_auth.py
```

### Magic Link Issues

#### Email not delivered
```yaml
Symptoms: User reports not receiving magic link
Debug:
  - Check SES sending limits (sandbox vs production)
  - Verify SPF/DKIM/DMARC DNS records
  - Check SES bounce/complaint lists
  - Test with verified email in sandbox mode
Code: backend/auth/email_provider.py
Docs: docs/SES_PRODUCTION_ACCESS.md, docs/EMAIL_SPAM_FIX.md
```

#### Token expired
```yaml
Symptoms: Magic link shows "expired" error
Debug:
  - Check token expiration time (default 30 min)
  - Verify server time synchronization
  - Check for clock skew between servers
Code: backend/auth/social_auth.py::generate_magic_link
```

### Session Issues

#### Session not persisting
```yaml
Symptoms: User logged out unexpectedly
Debug:
  - Check cookie settings (HttpOnly, Secure, SameSite)
  - Verify session storage (Redis/database)
  - Check session timeout configuration
Code: backend/api/auth.py, frontend/middleware.ts
```

## Warp Commands

```bash
# Test authentication flows
warp test auth                    # Test all auth flows
warp test auth:oauth             # Test OAuth only
warp test auth:magic-link        # Test magic link only

# Debug authentication
warp debug auth                   # Run auth diagnostics
warp debug auth:oauth            # Debug OAuth issues
warp debug auth:magic-link       # Debug magic link issues

# Monitor authentication
warp monitor auth                 # Monitor auth in real-time
warp monitor auth:failures       # Monitor only failures

# Configuration checks
warp check auth:oauth-config     # Check OAuth provider config
warp check auth:ses-config       # Check SES configuration
warp check auth:env-vars         # Check required environment variables
```

## Pieces MCP Integration

The Auth Flow Agent syncs with Pieces MCP to:
- **Share auth patterns**: Common flows and solutions
- **Track insights**: Debugging discoveries across sessions
- **Maintain knowledge**: Build auth troubleshooting knowledge base

### Privacy Preservation
- **Never sync PII**: No personal data, emails, or tokens
- **Anonymize identifiers**: All user IDs anonymized
- **Hash sensitive data**: Security-relevant data hashed before sync

### Sync Events
```yaml
Synced to Pieces:
  - Authentication failures (anonymized)
  - OAuth flow completions
  - Magic link generation events
  - Session creation events
  - Issue resolutions and patterns
```

## Environment Variables

### Required for OAuth
```bash
FACEBOOK_CLIENT_ID=your_facebook_client_id
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
SOCIAL_AUTH_REDIRECT_URI=https://yourdomain.com/api/social-auth/callback
```

### Required for Email (SES)
```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
SES_FROM_EMAIL=noreply@yourdomain.com
SES_VERIFIED_EMAILS=test@example.com  # For sandbox mode
```

### Required for Sessions
```bash
SESSION_SECRET=your_session_secret
SESSION_COOKIE_DOMAIN=.yourdomain.com
SESSION_COOKIE_SECURE=true
REDIS_URL=redis://localhost:6379  # For production
```

## Testing & Validation

### Security Checklist
- [ ] HTTPS enforced in production
- [ ] CSRF protection enabled (state parameter)
- [ ] Rate limiting configured (5 requests/hour for magic links)
- [ ] Tokens expire appropriately (30 min for magic links)
- [ ] One-time use tokens enforced

### Anonymity Checklist
- [ ] No PII in `anonymous_id`
- [ ] Identity stored separately from session data
- [ ] Zero-knowledge architecture maintained
- [ ] User can delete identity link at any time

### Functionality Checklist
- [ ] OAuth flows complete successfully
- [ ] Magic links delivered and verified
- [ ] Sessions persist across requests
- [ ] Anonymous sessions work without authentication

## Agent Coordination

The Auth Flow Agent coordinates with:

### Identity Proxy Agent
- **Anonymous session management**: Delegates to identity-proxy for session creation
- **Zero-knowledge enforcement**: Ensures no PII leakage

### Security Agent
- **Security validation**: CSRF, rate limiting, token security
- **Breach detection**: Monitors for suspicious activity

### Pieces Agent
- **Knowledge sync**: Shares auth patterns and solutions
- **Context preservation**: Maintains debugging context across sessions

## Escalation Rules

### Automatic Escalation
- **Cannot resolve after 3 attempts**: Escalate to human review
- **Potential security breach**: Immediate escalation + logging
- **Breaking change needed**: Human approval required

### Manual Escalation
```bash
# Escalate current auth issue
warp escalate auth-issue --reason "description of issue"

# Request human review
warp request-review auth-flow --context "additional context"
```

## Health Monitoring

### Auth Health Endpoint
```bash
# Check auth system health
curl http://localhost:8000/api/auth/health
```

### Health Checks
- Database connection
- Redis connection (if used)
- SES availability
- OAuth provider connectivity

### Alerts
- **Auth failure rate > 10%**: Alert Warp agent
- **Magic link delivery rate < 90%**: Check SES configuration
- **Session creation failures**: Check database/Redis

## Documentation References

### Internal Docs
- `docs/MAGIC_LINK_AUTHENTICATION.md`: Magic link implementation
- `docs/MAGIC_LINK_SECURITY.md`: Security considerations
- `docs/SES_PRODUCTION_ACCESS.md`: SES production setup
- `docs/EMAIL_SPAM_FIX.md`: Email deliverability
- `business/identity-proxy/README.md`: Anonymous identity architecture
- `business/identity-proxy/flows.yaml`: Identity flow definitions

### Code References
- `backend/api/auth.py`: Auth API endpoints
- `backend/api/social_auth.py`: Social auth API
- `backend/auth/social_auth.py`: Social auth implementation
- `backend/auth/anonymous_identity.py`: Anonymous identity manager
- `backend/auth/email_provider.py`: Email/magic link provider
- `backend/auth/oauth_providers.py`: OAuth provider configuration
- `frontend/app/auth/page.tsx`: Auth UI
- `frontend/app/auth/magic-link/page.tsx`: Magic link UI

## Change Log

### v1.0 (2025-11-22)
- Initial auth flow agent configuration
- Account-level scope for zsbw@proton.me
- OAuth, magic link, SMS/VoIP flows defined
- Issue catalog created
- Warp integration configured
- Pieces MCP sync enabled

## Support

For auth flow issues:
1. Check this README for common issues
2. Review `auth-flow-agent.yaml` for detailed flows
3. Run Warp diagnostics: `warp debug auth`
4. Check logs: `tail -f backend/logs/auth.log`
5. Escalate if unresolved: `warp escalate auth-issue`

---

**Account**: zsbw@proton.me  
**Scope**: Account-level authentication (not personal identity)  
**Agent Type**: auth_flow_specialist  
**Version**: 1.0
