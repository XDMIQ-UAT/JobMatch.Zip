# Platform Health Prompt Template

## Context

Creating health checks, monitoring, and operational runbooks. Privacy-preserving metrics.

## Pattern

Reference: `business/health/checks.yaml`, `scripts/health-check.ps1`

## Health Check Structure

```python
def check_platform_health():
    """
    System health check without exposing user data.
    
    Checks:
    - Database connectivity
    - Redis availability
    - Elasticsearch cluster health
    - Ollama LLM service
    - Backend API responsiveness
    - Frontend serving
    
    Returns aggregate metrics only (no individual user data).
    """
    return {
        "database": "healthy",
        "redis": "healthy",
        "elasticsearch": "healthy",
        "ollama": "healthy",
        "backend_api": "healthy",
        "frontend": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Metrics (Privacy-Preserving)

### System Metrics

- `anonymous_sessions_active`: count (no IDs)
- `assessments_completed_today`: count
- `matches_generated_last_hour`: count
- `checkpoint_success_rate`: percentage
- `human_review_queue_depth`: count
- `ollama_response_time_p99`: milliseconds

### Business Metrics

- `capability_assessments_total`: count
- `xdmiq_assessments_completed`: count
- `matches_created`: count
- `matches_accepted`: count (if user provides feedback)

## Constraints

- NEVER log individual anonymous_ids in metrics
- NEVER correlate metrics across users
- Aggregate only (counts, percentages, distributions)
- Privacy-preserving monitoring

## Runbook Structure

```yaml
incidents:
  - name: database_connection_failure
    severity: critical
    steps:
      1. Check database container health
      2. Verify network connectivity
      3. Check database logs
      4. Restore from checkpoint if needed
      5. Escalate if unresolved
```

## Health Dashboard

- Real-time system status
- Historical metrics (aggregated)
- Alert thresholds
- Runbook links

## Integration

- Health checks run every 30 seconds
- Metrics stored in time-series format
- Dashboards at `/admin/health`
- Alerts via webhook (optional)

