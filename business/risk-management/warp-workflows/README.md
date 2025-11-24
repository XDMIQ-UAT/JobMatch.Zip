# Cybersecurity Agent - Risk Management Office

## Overview

The Cybersecurity Agent is a specialized Warp agent owned by the Risk Management Office, responsible for platform-wide security monitoring, threat detection, vulnerability management, and compliance enforcement for the AI-Enabled LLC Matching Platform.

**Owner**: Risk Management Office  
**Scope**: Platform-wide cybersecurity  
**Agent Type**: cybersecurity_specialist  
**Version**: 1.0

## Purpose

This agent ensures the security and integrity of the platform while maintaining user privacy and zero-knowledge architecture. It monitors security threats, conducts vulnerability assessments, enforces compliance policies, and coordinates incident response.

## Core Responsibilities

1. **Security Monitoring**: Continuous monitoring for threats and vulnerabilities
2. **Vulnerability Management**: Regular scanning and patching of security issues
3. **Compliance Enforcement**: Ensure GDPR, CCPA, and privacy regulations compliance
4. **Incident Response**: Detect, contain, and remediate security incidents
5. **Security Audits**: Regular code reviews and security assessments
6. **Configuration Hardening**: Secure infrastructure and application configurations
7. **Threat Intelligence**: Stay updated on emerging security threats
8. **Documentation**: Maintain security policies and runbooks
9. **Privacy Protection**: Ensure privacy-preserving security measures
10. **Knowledge Sharing**: Sync security insights via Pieces MCP

## Security Domains

### 1. Application Security

**Focus**: Secure coding practices and application hardening

**Key Areas**:
- **Input Validation**: Prevent SQL injection, XSS, command injection, path traversal
- **Authentication Security**: Secure password hashing, token generation, session management
- **Authorization Security**: RBAC, least privilege, API endpoint authorization
- **API Security**: Rate limiting, request validation, CORS configuration
- **Data Security**: Encryption at rest/transit, PII isolation, secure key management

**Code Locations**:
```
backend/auth/**/*.py         # Authentication logic
backend/api/**/*.py          # API endpoints
backend/database/**/*.py     # Database connections
backend/models/**/*.py       # Data models
frontend/app/**/*.tsx        # Frontend code
frontend/lib/api/**/*.ts     # Frontend API calls
```

**Monitoring**:
- Brute force attempts
- Suspicious login patterns
- Unauthorized access attempts
- API abuse patterns
- Data exposure patterns

### 2. Infrastructure Security

**Focus**: Secure cloud infrastructure and configurations

**Key Areas**:
- **Network Security**: Firewall rules, network segmentation, VPC configuration
- **Container Security**: Secure Docker images, non-root execution, vulnerability scanning
- **Cloud Security**: IAM permissions (AWS, Oracle), S3 bucket policies, RDS security
- **Secrets Management**: No secrets in code, encrypted storage, rotation policies

**Locations**:
```
Dockerfile, Dockerfile.dev
docker-compose*.yml
kubernetes/manifests/**/*.yaml
.github/workflows/**/*.yml
.env (excluded from git)
secrets/ directory
```

**Monitoring**:
- Open ports and services
- Vulnerable dependencies
- Misconfigured cloud services
- Exposed secrets
- Public S3 buckets

### 3. Compliance & Privacy

**Focus**: Regulatory compliance and privacy protection

**Key Areas**:
- **Privacy Compliance**: GDPR, CCPA, right to be forgotten, data portability
- **Data Boundaries**: Identity vault isolation, anonymous data separation
- **Audit Logging**: Security events, access logs, change logs, incident logs

**References**:
```
business/policies/privacy.md
business/policies/data-boundaries.md
backend/logs/**/*.log
CloudWatch Logs
```

**Monitoring**:
- PII exposure
- Consent violations
- Data retention violations
- Identity linkage risks
- Log tampering

### 4. Threat Detection & Response

**Focus**: Identify and respond to security threats

**Key Areas**:
- **Vulnerability Scanning**: npm audit, pip-audit, Trivy, OWASP ZAP
- **Dependency Management**: Track CVEs, security advisories, supply chain risks
- **Intrusion Detection**: Monitor for SQL injection, XSS, rate limit violations
- **Incident Response**: Containment, investigation, remediation, post-incident review

**Tools**:
```bash
npm audit                    # Frontend dependencies
pip-audit                    # Backend dependencies
bandit -r backend/           # Python security
semgrep --config=auto .      # Multi-language patterns
trivy image <image>          # Container scanning
gitleaks detect              # Secret scanning
trufflehog git file://.      # Exposed credentials
```

**Response Times**:
- Critical (CVSS 9.0-10.0): Patch immediately
- High (CVSS 7.0-8.9): Patch within 7 days
- Medium (CVSS 4.0-6.9): Patch within 30 days
- Low (CVSS 0.1-3.9): Patch next release

## Workflows

### Security Assessment Workflow

1. **Identify Scope**
   - Code changes
   - Infrastructure changes
   - New dependencies
   - Configuration updates

2. **Run Automated Scans**
   ```powershell
   # Static analysis
   bandit -r backend/
   semgrep --config=auto .
   
   # Dependency scanning
   npm audit
   pip-audit
   
   # Container scanning
   trivy image jobmatch-backend
   
   # Secret scanning
   gitleaks detect
   ```

3. **Manual Review**
   - Authentication/authorization logic
   - Sensitive data handling
   - API security
   - Infrastructure configuration

4. **Document Findings**
   - Create security assessment report
   - File: `business/risk-management/reports/YYYY-MM-DD-assessment.md`

### Vulnerability Response Workflow

1. **Triage Vulnerability**
   - Assess severity (CVSS score)
   - Determine exploitability
   - Classify: Critical, High, Medium, Low

2. **Determine Impact**
   - Affected components
   - User data exposure risk
   - Service availability impact
   - Privacy implications

3. **Plan Remediation**
   - Update dependency
   - Apply patch
   - Configuration change
   - Code modification
   - Workaround/mitigation

4. **Execute Fix**
   - Test in development
   - Review security implications
   - Deploy to production
   - Verify fix

5. **Document Resolution**
   - File: `business/risk-management/reports/vulnerabilities/CVE-YYYY-NNNNN.md`

### Incident Response Workflow

1. **Detect Incident**
   - Automated alerts
   - User reports
   - Log analysis
   - Monitoring tools

2. **Contain Threat**
   ```powershell
   # Block malicious IPs
   warp security-block-ip <ip>
   
   # Disable compromised accounts
   warp security-disable-account <account>
   
   # Isolate affected systems
   # Preserve evidence
   ```

3. **Investigate**
   - Determine attack vector
   - Identify affected systems
   - Assess data exposure
   - Create timeline

4. **Remediate**
   - Patch vulnerability
   - Restore from backup
   - Reset credentials
   - Update security controls

5. **Post-Incident Review**
   - Create incident report
   - Document lessons learned
   - Implement process improvements
   - Update policies and runbooks

## Security Best Practices

### Secure Coding Principles

1. **Input Validation**: Validate all inputs at the boundary
2. **Parameterized Queries**: Never concatenate strings in SQL queries
3. **Output Encoding**: Escape output based on context (HTML, URL, JS)
4. **Secure Random**: Use cryptographically secure random for tokens
5. **No Sensitive Logging**: Never log tokens, passwords, or PII
6. **Fail Securely**: Deny by default
7. **Minimize Attack Surface**: Disable unused features
8. **Update Dependencies**: Keep all dependencies current

### Authentication & Authorization

1. **Strong Hashing**: Use bcrypt or argon2 for passwords
2. **Rate Limiting**: Implement on all auth endpoints
3. **Secure Tokens**: Use cryptographically secure token generation
4. **Session Management**: Appropriate expiration, secure cookies
5. **CSRF Protection**: Implement CSRF tokens
6. **Cookie Security**: HttpOnly, Secure, SameSite=Strict
7. **Least Privilege**: Enforce minimum necessary permissions
8. **Audit Logging**: Log all authentication events

### Privacy & Data Protection

1. **Zero-Knowledge**: Maintain zero-knowledge architecture
2. **PII Isolation**: Keep PII in identity vault only
3. **Anonymous IDs**: Use anonymous IDs everywhere else
4. **Encryption**: Encrypt sensitive data at rest and in transit
5. **TLS/HTTPS**: All connections must use TLS
6. **Data Retention**: Implement and enforce retention policies
7. **Right to be Forgotten**: Support data deletion requests
8. **No Correlation**: Never link anonymous IDs to identity without consent

### Infrastructure Security

1. **Least Privilege**: Apply to all IAM permissions
2. **Encryption**: Enable at rest and in transit
3. **Network Segmentation**: Implement proper segmentation
4. **Security Groups**: Use restrictive security groups
5. **Audit Logging**: Enable CloudWatch and audit logs
6. **Container Scanning**: Regularly scan for vulnerabilities
7. **Non-Root Containers**: Run containers as non-root user
8. **Secret Rotation**: Rotate secrets regularly

## Security Monitoring

### Real-time Monitoring

Monitor continuously for:
- Authentication failures (threshold: < 5% of attempts)
- API rate limit violations
- SQL injection attempts
- XSS attempts
- Command injection attempts
- Unauthorized access attempts
- Suspicious file uploads
- Unusual traffic patterns

### Security Metrics

| Metric | Threshold | Frequency | Action |
|--------|-----------|-----------|--------|
| Authentication failure rate | < 5% | Real-time | Alert if exceeded |
| Vulnerability count | 0 critical, < 5 high | Weekly | Monthly review |
| Time to patch critical | < 24 hours | Per incident | Track and improve |
| Security incident count | < 1 per month | Monthly | Root cause analysis |
| Failed authorization | < 1% of requests | Real-time | Alert if exceeded |

### Health Checks

**Daily Checks**:
- TLS/HTTPS enforcement on all production endpoints
- No secrets exposed in code or logs

**Weekly Checks**:
- Dependency vulnerabilities (0 critical, < 5 high)
- Container security (no vulnerable base images)
- Cloud configuration (no misconfigurations)

## Warp Commands

### Security Scans

```powershell
# Comprehensive scan
warp security-scan-all

# Individual scans
warp security-scan-dependencies     # npm audit + pip-audit
warp security-scan-containers       # trivy
warp security-scan-secrets          # gitleaks
warp security-scan-code             # bandit + semgrep
```

### Vulnerability Management

```powershell
warp security-check-vulnerabilities # Check for known CVEs
warp security-patch-critical        # Auto-patch critical issues
warp security-report                # Generate security report
```

### Compliance Checks

```powershell
warp security-check-compliance      # Run all compliance checks
warp security-audit-privacy         # Privacy compliance audit
warp security-audit-logs            # Security log audit
```

### Incident Response

```powershell
warp security-incident-respond      # Trigger incident response
warp security-block-ip <ip>         # Block malicious IP
warp security-disable-account <id>  # Disable compromised account
warp security-review-incident <id>  # Review incident details
```

## Environment Variables

### Critical Security Variables

```bash
# Secrets (NEVER commit to git)
SESSION_SECRET=<cryptographically-secure-secret>
JWT_SECRET=<cryptographically-secure-secret>
ENCRYPTION_KEY=<cryptographically-secure-key>
AWS_ACCESS_KEY_ID=<aws-access-key>
AWS_SECRET_ACCESS_KEY=<aws-secret-key>

# OAuth Secrets (NEVER commit to git)
FACEBOOK_CLIENT_SECRET=<facebook-secret>
LINKEDIN_CLIENT_SECRET=<linkedin-secret>
GOOGLE_CLIENT_SECRET=<google-secret>
MICROSOFT_CLIENT_SECRET=<microsoft-secret>
APPLE_CLIENT_SECRET=<apple-secret>

# Security Settings
ALLOWED_ORIGINS=https://yourdomain.com
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=900
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict
```

## Agent Coordination

The Cybersecurity Agent coordinates with other platform agents:

```
Cybersecurity Agent (Risk Management)
    │
    ├─→ Auth Flow Agent
    │   └─ Security review of authentication flows
    │      Code: backend/auth/**/*.py
    │
    ├─→ Identity Proxy Agent
    │   └─ Privacy-preserving security measures
    │      Maintain zero-knowledge architecture
    │
    └─→ Pieces Agent
        └─ Security knowledge sync
           Share threat intelligence
```

### Escalation Rules

**Automatic Escalation**:
- **Critical vulnerability discovered** → Immediate notification to Risk Management
- **Active security incident** → Trigger incident response playbook
- **Compliance violation detected** → Escalate to legal/compliance team
- **Cannot resolve issue** → Human security expert review

**Manual Escalation**:
```powershell
warp escalate security-issue --reason "description"
warp request-review security --context "context"
```

## Pieces MCP Integration

The agent integrates with Pieces MCP for knowledge sharing:

**Sync Events** (anonymized):
- Security incidents
- Vulnerability discoveries
- Security assessments
- Patch deployments
- Configuration changes

**Context Sharing**:
- Security patterns
- Threat intelligence
- Security knowledge base
- Response coordination

**Privacy Preservation**:
- Never sync PII or secrets
- Anonymize all identifiers
- Hash sensitive data
- Redact credentials

## File Structure

```
business/risk-management/
├── warp-workflows/
│   ├── cybersecurity-agent.yaml      # Main agent configuration
│   ├── README.md                     # This file
│   ├── QUICK_REFERENCE.md            # Quick reference guide
│   ├── scan-security.yaml            # Security scan workflow
│   ├── check-vulnerabilities.yaml    # Vulnerability check workflow
│   ├── check-compliance.yaml         # Compliance check workflow
│   ├── audit-privacy.yaml            # Privacy audit workflow
│   ├── incident-response.yaml        # Incident response workflow
│   └── block-ip.yaml                 # IP blocking workflow
│
├── runbooks/
│   ├── data-breach.md                # Data breach response
│   ├── dos-attack.md                 # DoS attack response
│   ├── vulnerability-disclosure.md   # Vulnerability disclosure process
│   └── security-incident.md          # General security incident
│
├── reports/
│   ├── YYYY-MM-DD-assessment.md      # Security assessment reports
│   └── vulnerabilities/
│       └── CVE-YYYY-NNNNN.md         # Vulnerability reports
│
├── SECURITY_POLICY.md                # Platform security policy
├── VULNERABILITY_DISCLOSURE.md       # Vulnerability disclosure policy
└── INCIDENT_RESPONSE.md              # Incident response procedures
```

## Getting Started

### Activation

```powershell
# Activate the cybersecurity agent
pwsh scripts/activate-cybersecurity-agent.ps1

# Verify activation
warp security-check-status
```

### Initial Security Scan

```powershell
# Run comprehensive security scan
warp security-scan-all

# Review findings
warp security-report
```

### Regular Operations

**Daily**:
- Monitor security alerts
- Review authentication logs
- Check for critical vulnerabilities

**Weekly**:
- Run automated security scans
- Review security metrics
- Check for dependency updates

**Monthly**:
- Conduct security assessment
- Review and update policies
- Test incident response procedures

## Documentation References

### Internal Documentation
- `business/policies/privacy.md` - Privacy policy
- `business/policies/data-boundaries.md` - Data boundaries
- `business/risk-management/SECURITY_POLICY.md` - Security policy
- `business/risk-management/VULNERABILITY_DISCLOSURE.md` - Disclosure policy
- `business/risk-management/INCIDENT_RESPONSE.md` - Incident response

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Support & Contact

For security concerns or questions:

1. Check this README and QUICK_REFERENCE.md
2. Review the agent configuration: `cybersecurity-agent.yaml`
3. Run diagnostics: `warp security-scan-all`
4. Check logs: `backend/logs/security.log`
5. Escalate if needed: `warp escalate security-issue`

**Emergency Security Contact**: Risk Management Office

---

**Version**: 1.0  
**Last Updated**: 2025-11-22  
**Owner**: Risk Management Office  
**License**: Internal Use Only
