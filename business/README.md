# Business Folder

**Purpose**: "Keep all platform components healthy and happy"

This folder contains operational assets for managing the platform itself—not the application code, but the business of running the platform.

## Structure

### `nouns/` - Entities
Business objects and data structures:
- **capabilities/**: Capability taxonomy, skill definitions
- **roles/**: Job role definitions, requirement templates
- **jobs/**: Job listing schemas, matching criteria
- **assessments/**: Assessment definitions, question banks
- **sessions/**: Session management policies, lifecycle

### `verbs/` - Actions
Operational workflows:
- Assess (capability assessment workflows)
- Match (job matching algorithms)
- Notify (communication templates)
- Checkpoint (backup/recovery procedures)
- Recover (disaster recovery playbooks)

### `identity-proxy/` - Anonymous Identity Management
- **flows/**: Anonymous session creation, voluntary identification flows
- **policies/**: Zero-knowledge rules, consent management, privacy boundaries

### `xdmiq/` - Preference-Based Assessment System
- **questions/**: Question banks by capability domain (YAML format)
- **scoring/**: Scoring schemas, weight calculations, normalization rules

### `health/` - Platform Health Monitoring
- Health check definitions
- Dashboard configurations
- Alert thresholds
- Privacy-preserving metrics

### `runbooks/` - Operational Playbooks
- Incident response procedures
- Scaling playbooks
- Maintenance guides
- Troubleshooting guides

### `metrics/` - Business Metrics
- KPI definitions
- OKR tracking
- Growth metrics
- Platform health indicators
- **Note**: All metrics are aggregate only (no individual user tracking)

### `policies/` - Platform Policies
- Privacy-by-default rules
- Data retention policies
- Consent management
- Compliance documentation

## Usage

### For Developers
When building features, reference business assets:
```python
# Load capability taxonomy
from business.nouns.capabilities import taxonomy

# Load XDMIQ questions
from business.xdmiq.questions import get_questions_for_domain

# Check health policies
from business.health import get_alert_threshold
```

### For Operators
Daily operations reference:
1. **Morning**: Check `business/health/` dashboards
2. **Incidents**: Follow `business/runbooks/`
3. **Metrics**: Review `business/metrics/` KPIs
4. **Updates**: Modify `business/xdmiq/questions/` or `business/policies/`

### For Business/Product
Update operational definitions:
- Add new capabilities to `nouns/capabilities/`
- Create new assessment questions in `xdmiq/questions/`
- Define new metrics in `metrics/`
- Update policies in `policies/`

## Claude Code Integration

The business folder is referenced by Claude Code hooks:
- `generate_capability_flow`: Uses `business/nouns/capabilities/`
- `generate_xdmiq_questions`: Uses `business/xdmiq/`
- `generate_identity_proxy`: Uses `business/identity-proxy/`
- `generate_platform_health`: Uses `business/health/`

Load context:
```powershell
python .claude-code\context-loader.py --hook generate_xdmiq_questions "Add problem-solving questions"
```

## File Formats

- **YAML** for configurations and definitions (easy to read/edit)
- **Markdown** for runbooks and documentation
- **JSON** for structured data (when programmatic access needed)

## Privacy Guardrails

**All business folder content must respect**:
- Anonymous-first design (no user identity references)
- Aggregate metrics only (no individual tracking)
- Zero-knowledge architecture (platform cannot reverse-engineer identity)
- Explicit consent for any identity linking

## Examples

### Capability Definition
```yaml
# business/nouns/capabilities/technical-skills.yaml
domain: Technical Skills
categories:
  - id: backend-development
    name: Backend Development
    skills:
      - Python
      - FastAPI
      - Database Design
    assessment_type: portfolio + practical
```

### XDMIQ Question
```yaml
# business/xdmiq/questions/problem-solving.yaml
domain: Problem Solving
questions:
  - id: ps-001
    text: "Which approach do you prefer when debugging?"
    options:
      - Add logging statements
      - Use a debugger
      - Review recent changes
      - Ask a colleague
    follow_up: "Why does that work better for you?"
```

### Health Check
```yaml
# business/health/database.yaml
check:
  name: PostgreSQL Health
  endpoint: /health/database
  interval: 30s
  metrics:
    - connection_pool_usage
    - query_latency_p99
  alert_threshold: 3 consecutive failures
```

### Runbook
```markdown
# business/runbooks/high-latency.md

## Incident: API Latency >500ms

### Symptoms
- Slow page loads
- Timeouts
- Queue backup

### Diagnosis
1. Check Elasticsearch health
2. Check Redis cache hit rate
3. Review slow query log

### Resolution
1. Scale Elasticsearch
2. Increase cache size
3. Optimize queries
```

## Contributing

When adding business assets:
1. Follow existing file structure
2. Use YAML for configs, Markdown for docs
3. Include examples in definitions
4. Test with Claude Code hooks
5. Update this README if adding new top-level folders

---

**Maintained by**: Platform Operations Team  
**Last Updated**: 2025-01-22  
**Version**: 1.0
