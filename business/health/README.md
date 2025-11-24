# Health - Health Checks and Dashboards

This folder contains health check configurations and dashboard definitions for platform monitoring.

## Purpose

Monitor platform health and operational metrics:
- **Health Checks**: System component health monitoring (database, Redis, Elasticsearch, Ollama)
- **Dashboards**: Operational visibility dashboards
- **Privacy-Preserving**: Aggregate data only (no individual user tracking)

## Key Principles

- **Privacy-Preserving**: Never log individual anonymous_ids in metrics
- **Aggregate Only**: Counts, percentages, distributions (no user-level data)
- **Operational Visibility**: Monitor system health without compromising user privacy
- **No Identity Correlation**: Metrics cannot correlate across users

## Files

- `checks/` - Health check YAML definitions
- `dashboards.md` - Dashboard configuration templates

## Health Check Format

```yaml
check:
  name: PostgreSQL Health
  endpoint: /health/database
  interval: 30s
  alert_threshold: 3 consecutive failures
  metrics:
    - connection_pool_size
    - query_latency_p99
    - active_connections
  privacy: No individual user data logged
```

## Monitored Components

- **PostgreSQL**: Database health, connection pool, query latency
- **Redis**: Cache health, hit rate, memory usage
- **Elasticsearch**: Search index health, query performance
- **Ollama**: LLM service health, response times
- **API**: Endpoint latency, error rates, throughput

## Metrics Guidelines

### Allowed Metrics
- Aggregate counts (anonymous_sessions_active, assessments_completed_today)
- Percentages (checkpoint_success_rate, cache_hit_rate)
- Distributions (latency_p99, response_time_distribution)
- System metrics (CPU, memory, disk usage)

### Prohibited Metrics
- Individual anonymous_ids
- User-level tracking
- Cross-user correlation
- Identity-linked metrics

## Related Code

- `backend/api/health.py` - Health check endpoints (if exists)
- Monitoring infrastructure configurations

