# Guardian Agents - Quick Reference

**Location**: `.warp/agents/`  
**Purpose**: Specialized AI agents for code review, compliance, and infrastructure safety

---

## Available Guardian Agents

### 1. Infrastructure Guardian 🏗️
**File**: `infrastructure-guardian.md`  
**Focus**: State management, checkpointing, deployment safety

**When to Invoke**:
- Before production deployments
- During database migrations
- When troubleshooting infrastructure issues
- For disaster recovery planning

**Key Commands**:
```powershell
.\scripts\checkpoint.ps1 -CheckpointName "pre-deploy" -IncludeDatabase -IncludeRedis
.\scripts\infra-agent.ps1 verify
.\scripts\recover.ps1 -List
```

---

### 2. Compliance Guardian 🔒
**File**: `compliance-guardian.md`  
**Focus**: HIPAA, PII protection, privacy, security standards

**When to Invoke**:
- Before handling user data
- When implementing authentication
- For security audits
- Before public release

**Key Checks**:
- No PII in logs
- Secrets management
- API endpoint security
- Data retention policies

---

### 3. Data Governance Guardian 📊
**File**: `data-governance-guardian.md`  
**Focus**: Anonymous-first architecture, data boundaries, zero-knowledge

**When to Invoke**:
- When designing data models
- Before adding user-facing features
- For data boundary audits
- When integrating third-party services

**Key Principles**:
- Anonymous IDs only
- No identity correlation
- Separate identity tables
- Zero-knowledge compliance

---

### 4. Brand & UX Guardian 🎨
**File**: `SaM-brand-ux-guardian.md`  
**Focus**: Brand consistency, design system, accessibility, user experience

**When to Invoke**:
- Before deploying UI changes
- For marketing campaign reviews
- During design system updates
- For accessibility audits

**Key Checks**:
- Brand color compliance
- WCAG accessibility
- Mobile responsiveness
- Performance (CLS, LCP, FID)

---

## Integration Workflow

### Pre-Deployment Checklist (ALL AGENTS)

```powershell
# 1. Infrastructure Guardian - Create checkpoint
.\scripts\checkpoint.ps1 -CheckpointName "pre-prod" -IncludeDatabase -IncludeRedis -Compress

# 2. Infrastructure Guardian - Verify services
.\scripts\infra-agent.ps1 verify

# 3. Compliance Guardian - Review checklist
# - Check logs for PII leakage
# - Verify secrets management
# - Validate API security
# - Confirm data retention

# 4. Data Governance Guardian - Review checklist
# - Verify anonymous-first boundaries
# - Check zero-knowledge compliance
# - Audit data storage patterns
# - Validate third-party integrations

# 5. Brand/UX Guardian - Review checklist
# - Brand color compliance
# - Accessibility standards
# - Mobile responsiveness
# - Performance metrics

# 6. Deploy only if ALL checks pass ✅
```

---

## Emergency Response

### Critical Infrastructure Failure
**Primary Agent**: Infrastructure Guardian  
**Action**:
```powershell
.\scripts\recover.ps1 -CheckpointName "last-known-good" -Force
.\scripts\infra-agent.ps1 verify
```

### Security Incident
**Primary Agent**: Compliance Guardian  
**Action**:
- Review PII exposure
- Check audit logs
- Validate secrets rotation
- Notify team immediately

### Data Boundary Violation
**Primary Agent**: Data Governance Guardian  
**Action**:
- Identify violation source
- Remove exposed data
- Audit correlation paths
- Implement fixes

### UX Breaking Change
**Primary Agent**: Brand/UX Guardian  
**Action**:
- Document visual regressions
- Rollback if critical
- Fix and re-test
- Update design system

---

## Agent Interaction Matrix

| Scenario | Primary Agent | Supporting Agents |
|----------|--------------|-------------------|
| Production Deploy | Infrastructure | All (pre-deploy checks) |
| Database Migration | Infrastructure | Data Governance |
| New Feature | Brand/UX | Data Governance, Compliance |
| Authentication Change | Compliance | Data Governance, Infrastructure |
| Third-party Integration | Data Governance | Compliance |
| UI/UX Update | Brand/UX | Infrastructure (checkpoint) |

---

## Quick Agent Selection

**Ask yourself:**

- **Is it about infrastructure/deployment?** → Infrastructure Guardian
- **Does it involve user data?** → Data Governance Guardian
- **Does it handle PII/security?** → Compliance Guardian
- **Does it affect UI/brand?** → Brand/UX Guardian

**Multiple concerns?** → Invoke multiple agents in sequence

---

## Success Metrics (All Agents)

- ✅ 100% deployment checkpoint compliance
- ✅ Zero PII leakage incidents
- ✅ Zero data boundary violations
- ✅ >95% brand consistency score
- ✅ <15 minute mean time to recovery (MTTR)
- ✅ 100% accessibility compliance (WCAG AA)

---

## Agent Activation Examples

### Example 1: Adding User Profile Feature
```
1. Data Governance Guardian - Design data model (anonymous-first)
2. Compliance Guardian - Review PII handling
3. Brand/UX Guardian - Review profile UI
4. Infrastructure Guardian - Checkpoint before deploy
```

### Example 2: Database Schema Change
```
1. Infrastructure Guardian - Create pre-migration checkpoint
2. Data Governance Guardian - Verify data boundaries
3. Infrastructure Guardian - Execute migration safely
4. Infrastructure Guardian - Verify post-migration
```

### Example 3: Emergency Rollback
```
1. Infrastructure Guardian - Immediate checkpoint recovery
2. All Guardians - Post-incident review
3. Infrastructure Guardian - Post-mortem documentation
```

---

## Best Practices

1. **Always checkpoint before risky changes** (Infrastructure Guardian)
2. **Never log PII in plaintext** (Compliance Guardian)
3. **Maintain anonymous-first architecture** (Data Governance Guardian)
4. **Test across devices and screen readers** (Brand/UX Guardian)
5. **Document all guardian findings** (All Agents)
6. **Run pre-deployment checks in sequence** (All Agents)
7. **Test recovery procedures regularly** (Infrastructure Guardian)

---

## Resources

- **WARP.md**: Complete development guide
- **CONTRIBUTING.md**: Development guidelines
- **ROADMAP.md**: Feature timeline
- **PROJECT_STATUS.md**: Current project state

---

**Remember**: Guardian agents are your safety net. Use them proactively, not reactively. Prevention is always better than recovery.

**"Trust, but verify. Then checkpoint."**
