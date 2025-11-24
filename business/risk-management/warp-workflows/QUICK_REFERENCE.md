# Cybersecurity Agent - Quick Reference

**Owner**: Risk Management Office  
**Scope**: Platform-wide cybersecurity monitoring and threat detection  
**Agent Type**: cybersecurity_specialist

## Quick Commands

```powershell
# Activate agent
pwsh scripts/activate-cybersecurity-agent.ps1

# Security scans
warp security-scan-all              # Run all security scans
warp security-scan-dependencies     # Scan dependencies for vulnerabilities
warp security-scan-containers       # Scan Docker images
warp security-scan-secrets          # Scan for exposed secrets
warp security-scan-code             # Static code analysis

# Vulnerability management
warp security-check-vulnerabilities # Check for known vulnerabilities
warp security-patch-critical        # Patch critical vulnerabilities
warp security-report                # Generate security report

# Compliance checks
warp security-check-compliance      # Run compliance checks
warp security-audit-privacy         # Privacy audit
warp security-audit-logs            # Security log audit

# Incident response
warp security-incident-respond      # Trigger incident response
warp security-block-ip <ip>         # Block malicious IP
warp security-review-incident       # Review security incident
```

## Security Domains

### 1. Application Security

```
Input Validation → Authentication → Authorization → API Security → Data Protection
```

**Key Concerns**:
- SQL injection, XSS, CSRF prevention
- Secure password hashing (bcrypt/argon2)
- Cryptographically secure tokens
- Rate limiting on all endpoints
- Encryption at rest and in transit

**Code Locations**:
- `backend/auth/**/*.py` - Authentication logic
- `backend/api/**/*.py` - API endpoints
- `frontend/app/**/*.tsx` - Frontend code

### 2. Infrastructure Security

```
Network Security → Container Security → Cloud Security → Secrets Management
```

**Key Concerns**:
- Firewall rules and network segmentation
- Non-root container execution
- IAM least privilege (AWS, Oracle Cloud)
- No secrets in code or git history

**Locations**:
- `Dockerfile`, `docker-compose*.yml`
- `kubernetes/manifests/**/*.yaml`
- `.env` (excluded from git)

### 3. Compliance & Privacy

```
Privacy Compliance → Data Boundaries → Audit Logging
```

**Key Concerns**:
- GDPR, CCPA compliance
- Zero-knowledge architecture
- Identity vault isolation
- Comprehensive audit trails

**References**:
- `business/policies/privacy.md`
- `business/policies/data-boundaries.md`

### 4. Threat Detection & Response

```
Vulnerability Scanning → Dependency Management → Intrusion Detection → Incident Response
```

**Key Tools**:
- `npm audit`, `pip-audit` - Dependency scanning
- `trivy` - Container scanning
- `bandit`, `semgrep` - Static analysis
- `gitleaks`, `trufflehog` - Secret scanning

## Common Security Issues

### Application Security Issues

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| SQL Injection | Malformed queries | Use parameterized queries |
| XSS | Script injection | Escape output, validate input |
| CSRF | Unauthorized actions | Implement CSRF tokens |
| Weak passwords | Easy to guess | Enforce strong password policy |
| Token reuse | Session hijacking | One-time tokens, expiration |

### Infrastructure Issues

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| Exposed secrets | Credentials in code | Use environment variables |
| Vulnerable dependencies | CVE alerts | Update dependencies |
| Open ports | Unnecessary services | Restrict firewall rules |
| Privileged containers | Root execution | Run as non-root user |
| Public S3 buckets | Data exposure | Restrict bucket policies |

### Compliance Issues

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| PII in logs | Identity exposure | Anonymize logs |
| No consent | GDPR violation | Implement consent management |
| Data retention | Stale data | Enforce retention policies |
| Identity linkage | Privacy risk | Maintain data boundaries |

## Security Scanning Workflow

```powershell
# 1. Run automated scans
npm audit                           # Frontend dependencies
pip-audit                           # Backend dependencies
bandit -r backend/                  # Python security issues
semgrep --config=auto .             # Multi-language patterns
trivy image jobmatch-backend        # Container vulnerabilities
gitleaks detect                     # Secret scanning

# 2. Review findings
warp security-report                # Generate report

# 3. Triage vulnerabilities
# - Critical (CVSS 9.0-10.0): Patch immediately
# - High (CVSS 7.0-8.9): Patch within 7 days
# - Medium (CVSS 4.0-6.9): Patch within 30 days
# - Low (CVSS 0.1-3.9): Patch next release

# 4. Apply fixes
warp security-patch-critical        # Auto-patch critical issues

# 5. Verify fixes
# Re-run scans to confirm remediation
```

## Incident Response Workflow

```
Detection → Containment → Investigation → Remediation → Post-Incident Review
```

### Quick Response Steps

```powershell
# 1. Detect incident
# - Monitor alerts, logs, user reports

# 2. Contain threat
warp security-block-ip <malicious-ip>
warp security-disable-account <compromised-account>

# 3. Investigate
warp security-review-incident --id <incident-id>
# - Check logs: backend/logs/auth.log
# - Review CloudWatch
# - Analyze attack vector

# 4. Remediate
warp security-patch-vulnerability --cve <CVE-ID>
# - Reset credentials
# - Restore from backup
# - Update security controls

# 5. Post-incident review
# - Create incident report
# - Document lessons learned
# - Update runbooks
```

## Security Monitoring

### Real-time Monitoring

Monitor for:
- Authentication failures (> 5% of attempts)
- API rate limit violations
- SQL injection attempts
- XSS attempts
- Command injection attempts
- Unauthorized access attempts
- Suspicious file uploads
- Unusual traffic patterns

### Security Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| Authentication failure rate | < 5% | Alert if exceeded |
| Vulnerability count | 0 critical, < 5 high | Monthly review |
| Time to patch critical | < 24 hours | Track and improve |
| Security incidents | < 1 per month | Root cause analysis |
| Failed authorization | < 1% of requests | Alert if exceeded |

### Health Checks

```powershell
# Daily checks
warp security-check-https           # TLS/HTTPS enforcement
warp security-check-secrets         # No secrets exposed

# Weekly checks
warp security-check-vulnerabilities # Dependency vulnerabilities
warp security-check-containers      # Container security
warp security-check-cloud-config    # Cloud misconfigurations
```

## Security Best Practices

### Secure Coding Checklist

- [ ] Validate all inputs at the boundary
- [ ] Use parameterized queries (no string concatenation)
- [ ] Escape output based on context (HTML, URL, JS)
- [ ] Use secure random for security-sensitive values
- [ ] Never log sensitive data (tokens, passwords, PII)
- [ ] Fail securely (deny by default)
- [ ] Minimize attack surface (disable unused features)
- [ ] Keep dependencies up to date

### Authentication & Authorization Checklist

- [ ] Use strong password hashing (bcrypt/argon2)
- [ ] Implement rate limiting on auth endpoints
- [ ] Use cryptographically secure tokens
- [ ] Expire sessions appropriately
- [ ] Implement CSRF protection
- [ ] Use HttpOnly, Secure, SameSite cookies
- [ ] Enforce least privilege
- [ ] Log all authentication events

### Privacy & Data Protection Checklist

- [ ] Maintain zero-knowledge architecture
- [ ] Keep PII in identity vault only
- [ ] Use anonymous IDs everywhere else
- [ ] Encrypt sensitive data at rest
- [ ] Use TLS/HTTPS for all connections
- [ ] Implement data retention policies
- [ ] Support right to be forgotten
- [ ] Never correlate anonymous IDs to identity without consent

### Infrastructure Security Checklist

- [ ] Use principle of least privilege for IAM
- [ ] Enable encryption at rest and in transit
- [ ] Implement network segmentation
- [ ] Use security groups restrictively
- [ ] Enable audit logging (CloudWatch, etc.)
- [ ] Scan containers for vulnerabilities
- [ ] Run containers as non-root
- [ ] Rotate secrets regularly

## File Structure

```
business/risk-management/
├── warp-workflows/
│   ├── cybersecurity-agent.yaml  # Main agent config
│   ├── README.md                 # Full documentation
│   └── QUICK_REFERENCE.md        # This file
├── runbooks/
│   ├── data-breach.md            # Data breach response
│   ├── dos-attack.md             # DoS attack response
│   └── vulnerability-disclosure.md
├── reports/
│   ├── YYYY-MM-DD-assessment.md  # Security assessments
│   └── vulnerabilities/
│       └── CVE-YYYY-NNNNN.md     # Vulnerability reports
├── SECURITY_POLICY.md
├── VULNERABILITY_DISCLOSURE.md
└── INCIDENT_RESPONSE.md

backend/
├── auth/**/*.py                   # Authentication logic
├── api/**/*.py                    # API endpoints
├── database/**/*.py               # Database connections
└── models/**/*.py                 # Data models

Dockerfile, docker-compose*.yml
kubernetes/manifests/**/*.yaml
.github/workflows/**/*.yml
```

## Agent Coordination

```
Cybersecurity Agent (You Are Here)
    ↓
    ├─→ Auth Flow Agent
    │   └─ Security review of authentication flows
    │
    ├─→ Identity Proxy Agent
    │   └─ Privacy-preserving security measures
    │
    └─→ Pieces Agent
        └─ Security knowledge sync
```

## Environment Variables

### Critical Security Variables

```bash
# Secrets (NEVER commit)
SESSION_SECRET=xxx
JWT_SECRET=xxx
ENCRYPTION_KEY=xxx
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx

# OAuth secrets (NEVER commit)
FACEBOOK_CLIENT_SECRET=xxx
LINKEDIN_CLIENT_SECRET=xxx
GOOGLE_CLIENT_SECRET=xxx
MICROSOFT_CLIENT_SECRET=xxx
APPLE_CLIENT_SECRET=xxx

# Security settings
ALLOWED_ORIGINS=https://yourdomain.com
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=900
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict
```

## Escalation

### Automatic Escalation Triggers

- **Critical vulnerability discovered** → Immediate notification to Risk Management
- **Active security incident** → Trigger incident response playbook
- **Compliance violation detected** → Escalate to legal/compliance team
- **Cannot resolve security issue** → Human security expert review

### Manual Escalation

```powershell
warp escalate security-issue --reason "description"
warp request-review security --context "context"
```

## Key Principles

1. **Defense in depth**: Multiple layers of security
2. **Least privilege**: Minimum necessary permissions
3. **Privacy by design**: Zero-knowledge architecture
4. **Fail securely**: Deny by default
5. **Monitor continuously**: Real-time threat detection
6. **Respond quickly**: Critical patches within 24 hours
7. **Learn from incidents**: Post-incident reviews
8. **Stay updated**: Weekly vulnerability scans

## Documentation References

### Internal
- `business/policies/privacy.md` - Privacy policy
- `business/policies/data-boundaries.md` - Data boundaries
- `business/risk-management/SECURITY_POLICY.md` - Security policy
- `business/risk-management/VULNERABILITY_DISCLOSURE.md` - Vulnerability disclosure
- `business/risk-management/INCIDENT_RESPONSE.md` - Incident response

### External
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
- CWE Top 25: https://cwe.mitre.org/top25/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework

## Support

1. Check this quick reference
2. Review `README.md` for details
3. Check `cybersecurity-agent.yaml` for workflows
4. Run diagnostics: `warp security-scan-all`
5. Check logs: `backend/logs/security.log`
6. Escalate if needed

---

**Last Updated**: 2025-11-22  
**Version**: 1.0  
**Owner**: Risk Management Office
