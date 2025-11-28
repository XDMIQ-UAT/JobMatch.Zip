# UAT Content Monitoring System

## Overview
Critical security monitoring system for the UAT (User Acceptance Testing) environment to detect unexpected user content, PII leaks, and potential security incidents during the testing phase.

## 🚨 Critical Alert Types

### 1. **SENSITIVE_CONTENT**
- SSN, credit card numbers, phone numbers, emails
- Passwords, API keys, tokens
- Financial data (bank accounts, routing numbers)
- Medical records, prescriptions, diagnoses
- Personal identifiers

### 2. **UNEXPECTED_FILE**
- Files not matching expected patterns (.tsx, .ts, .json, .md)
- User uploads in UAT folders
- Binary files, executables, archives

### 3. **LARGE_FILE**
- Files exceeding 1MB (potential data dumps)
- Unusual file growth patterns

### 4. **SUSPICIOUS_ACTIVITY**
- Exploit keywords (XSS, SQL injection, backdoor)
- Security vulnerability indicators

## 🛡️ Monitored Locations

### Frontend
- `E:\zip-jobmatch\frontend\app\uat\`
- `E:\zip-jobmatch\frontend\app\uat\register\`
- `E:\zip-jobmatch\frontend\app\uat\scenarios\`
- `E:\zip-jobmatch\frontend\app\uat\earnings\`

### Backend (if exists)
- `E:\zip-jobmatch\backend\uat\`
- `E:\zip-jobmatch\backend\uat\uploads\`
- `E:\zip-jobmatch\backend\uat\data\`

### User Submission Directories (watched for creation)
- `*/uat/uploads/`
- `*/uat/submissions/`
- `*/uat/user-data/`

## 📋 Quick Start

### Start Monitoring (Recommended during UAT)
```powershell
# Start in a dedicated terminal window
.\scripts\monitor-uat-content.ps1

# Custom settings
.\scripts\monitor-uat-content.ps1 -IntervalSeconds 60  # Check every 60 seconds
```

### View Current Alerts
```powershell
# View recent alerts (last 10)
.\scripts\view-uat-alerts.ps1

# View all alerts
.\scripts\view-uat-alerts.ps1 -ShowAll

# Clear alerts after investigation
.\scripts\view-uat-alerts.ps1 -ClearAlerts
```

## 📊 Dashboard Output

### Clean State
```
✅ No alerts! UAT folder is clean!
```

### Alert State
```
╔═══════════════════════════════════════════════════╗
║         UAT MONITORING - ALERTS DASHBOARD        ║
╚═══════════════════════════════════════════════════╝

Total Alerts: 3
  Critical:   2
  Warnings:   1

🚨 ALERT: SENSITIVE_CONTENT
───────────────────────────────────────────────────
Time:     2025-11-25T18:45:21Z
File:     E:\zip-jobmatch\frontend\app\uat\page.tsx
Reason:   Detected pattern: \b\d{3}-\d{2}-\d{4}\b
Preview:  Test content with SSN: 123-45-6789...
```

## 🔍 What Gets Monitored

### Pattern Detection
- **Regex Patterns**: SSN, email, phone, credit cards
- **Keywords**: Sensitive terms (password, token, medical, etc.)
- **File Size**: Unusual growth or large files
- **File Types**: Unexpected extensions or formats

### Change Detection
- Files modified in last 5 minutes
- New files in UAT directories
- Creation of submission/upload folders

### Continuous Monitoring
- Scans every 30 seconds (configurable)
- Real-time logging to `logs/uat-monitor.log`
- JSON alert storage in `logs/uat-alerts.json`

## 🚦 Response Procedures

### CRITICAL Alert Response
1. **STOP** - Pause UAT testing immediately
2. **INVESTIGATE** - Review the flagged file/content
3. **CONTAIN** - If PII found, quarantine and sanitize
4. **NOTIFY** - Alert security team and stakeholders
5. **DOCUMENT** - Record incident details
6. **REMEDIATE** - Remove sensitive data, update procedures

### WARNING Alert Response
1. **REVIEW** - Check if alert is false positive
2. **VERIFY** - Confirm content is appropriate for UAT
3. **LOG** - Document decision to ignore or escalate
4. **MONITOR** - Watch for repeated patterns

## 📁 Log Files

### Monitor Log
- **Location**: `E:\zip-jobmatch\logs\uat-monitor.log`
- **Format**: `[timestamp] [LEVEL] message`
- **Levels**: INFO, WARNING, CRITICAL
- **Content**: All scan activities, changes detected

### Alerts JSON
- **Location**: `E:\zip-jobmatch\logs\uat-alerts.json`
- **Format**: JSON array of alert objects
- **Fields**: timestamp, type, file, contentSnippet, reason, severity
- **Persistence**: Cumulative until manually cleared

## 🔧 Configuration

### Adjust Scan Interval
```powershell
# Default: 30 seconds
.\scripts\monitor-uat-content.ps1 -IntervalSeconds 60  # Check every minute
```

### Custom Paths
```powershell
.\scripts\monitor-uat-content.ps1 `
    -UATPath "C:\custom\path\uat" `
    -LogPath "C:\custom\logs\monitor.log"
```

### Add Custom Patterns
Edit `scripts\monitor-uat-content.ps1` and add to `$SensitivePatterns` array:
```powershell
$SensitivePatterns = @(
    # Your custom patterns
    'company secret',
    '\bPROPRIETARY\b',
    # ... existing patterns
)
```

## 🔐 Security Best Practices

### During UAT
1. **Always run monitor** during active testing
2. **Review logs daily** even if no alerts
3. **Test with sanitized data** only
4. **Never use production data** in UAT
5. **Clear alerts** after investigation (not before!)

### After UAT
1. **Archive logs** before clearing
2. **Review all alerts** for patterns
3. **Update training** based on incidents
4. **Document lessons learned**
5. **Improve detection** rules as needed

## 🎯 Integration Points

### CI/CD Pipeline
```powershell
# Run quick scan before deployment
.\scripts\monitor-uat-content.ps1 -IntervalSeconds 0  # One-time scan
if ((Get-Content logs\uat-alerts.json | ConvertFrom-Json).Count -gt 0) {
    Write-Error "UAT alerts detected! Deployment blocked."
    exit 1
}
```

### Scheduled Tasks
```powershell
# Windows Task Scheduler
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
$action = New-ScheduledTaskAction -Execute "pwsh.exe" `
    -Argument "-File E:\zip-jobmatch\scripts\monitor-uat-content.ps1"
Register-ScheduledTask -TaskName "UAT-Monitor" -Trigger $trigger -Action $action
```

### Alert Notifications
Add to monitor script for email/Slack notifications:
```powershell
function Send-AlertNotification {
    param($Alert)
    # Send email via SendGrid
    # Post to Slack webhook
    # Log to external SIEM
}
```

## 📞 Escalation Contacts

### Critical Alert (Immediate)
- **Security Team**: security@jobmatch.zip
- **On-Call**: (626) 995-9974 (Twilio AI line - coming soon)
- **Incident Response**: Follow IR playbook

### Warning Alert (Review within 24h)
- **UAT Team Lead**: uat-lead@jobmatch.zip
- **Product Manager**: product@jobmatch.zip

## 🧪 Testing the Monitor

### Test with Safe Patterns (DO NOT use real data!)
```powershell
# Create a test file
"Test SSN: XXX-XX-XXXX" | Out-File -FilePath "frontend\app\uat\test-alert.txt"

# Monitor should detect pattern
# View alert
.\scripts\view-uat-alerts.ps1

# Clean up
Remove-Item "frontend\app\uat\test-alert.txt"
.\scripts\view-uat-alerts.ps1 -ClearAlerts
```

## 📚 Related Documentation
- [UAT Guide](./testing/UAT_GUIDE.md)
- [Security Audit Report](../SECURITY_AUDIT_REPORT.md)
- [Privacy Policy](./PRIVACY_POLICY.md)
- [Compliance Report](../COMPLIANCE_REPORT.md)

## 🔄 Maintenance

### Weekly Tasks
- [ ] Review accumulated alerts
- [ ] Update sensitive pattern list
- [ ] Check monitor is running
- [ ] Archive old logs (>30 days)

### Monthly Tasks
- [ ] Analyze false positive rate
- [ ] Update detection rules
- [ ] Security team review
- [ ] Update documentation

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-25  
**Status**: ✅ Production Ready  
**Criticality**: 🔴 HIGH - Required during UAT
