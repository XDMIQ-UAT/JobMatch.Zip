# 🚨 UAT MONITORING - QUICK REFERENCE

## ⚡ Critical Commands

### Start Monitor (Run This First!)
```powershell
.\scripts\monitor-uat-content.ps1
```
**Keep this running in a dedicated terminal during all UAT testing**

### Check for Alerts
```powershell
.\scripts\view-uat-alerts.ps1
```

### View All Alerts
```powershell
.\scripts\view-uat-alerts.ps1 -ShowAll
```

### Clear Alerts (After Investigation)
```powershell
.\scripts\view-uat-alerts.ps1 -ClearAlerts
```

---

## 🚦 Alert Levels

| Icon | Level | Action Required |
|------|-------|----------------|
| 🔴 | CRITICAL | **STOP TESTING** - Investigate immediately |
| 🟡 | WARNING | Review within 24 hours |
| 🟢 | INFO | Monitor for patterns |

---

## 🎯 What Triggers Alerts

### 🔴 CRITICAL
- SSN patterns (XXX-XX-XXXX)
- Credit card numbers
- Phone numbers in unexpected places
- Email addresses with real domains
- Keywords: password, api key, token, secret
- Financial data: bank account, routing number
- Medical: diagnosis, prescription, medical record
- Files > 1MB in UAT folders
- Suspicious keywords: exploit, injection, backdoor

### 🟡 WARNING
- Unexpected file types (.exe, .zip, .dat, etc.)
- New folders: uploads/, submissions/, user-data/
- Recent file modifications

---

## 📍 Monitored Locations

```
E:\zip-jobmatch\frontend\app\uat\
├── page.tsx
├── register\
│   └── page.tsx
├── scenarios\
│   └── page.tsx
└── earnings\
    └── page.tsx

E:\zip-jobmatch\backend\uat\  (if exists)
```

---

## 🆘 Emergency Response

### If CRITICAL Alert Appears:

1. **PAUSE** all UAT testing immediately
2. **SCREENSHOT** the alert
3. **DO NOT DELETE** the flagged content yet
4. **NOTIFY** security team: security@jobmatch.zip
5. **CALL** (626) 995-9974 if urgent (coming soon)
6. **DOCUMENT** what test was running when alert fired
7. **WAIT** for security clearance before resuming

### Quick Investigation:
```powershell
# See what file triggered it
.\scripts\view-uat-alerts.ps1

# Open the file (carefully!)
code "path\from\alert"

# Check if it's test data or real PII
# If real PII: ESCALATE IMMEDIATELY
# If test data: Document false positive, update patterns
```

---

## ✅ Daily Checklist

- [ ] Monitor script is running
- [ ] Check alerts: `.\scripts\view-uat-alerts.ps1`
- [ ] Review log: `logs\uat-monitor.log`
- [ ] No unexpected files in UAT folders
- [ ] No user submission directories created

---

## 📊 Current Status

**Last Checked**: 2025-11-25 18:45 UTC  
**Status**: ✅ Clean - No alerts  
**Monitor**: Ready to start  
**Alert Log**: Not yet created (will be at `logs\uat-alerts.json`)

---

## 🔗 Full Documentation

See: `docs\UAT_MONITORING.md`

---

## 💡 Pro Tips

1. **Run monitor in separate terminal** - Don't close it during UAT
2. **Check alerts before committing** - Prevent PII from entering git
3. **Use sanitized test data** - Never test with real user information
4. **Archive logs weekly** - Helps identify patterns over time
5. **Test the monitor** - Use safe dummy patterns to verify it works

---

**Questions?** Contact UAT Team Lead or Security Team  
**Emergency?** security@jobmatch.zip

---

*This is a critical security tool. Always run during UAT testing.*
