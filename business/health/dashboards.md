# Health Dashboards

Operational visibility dashboards for platform monitoring. All dashboards follow privacy-preserving principles (aggregate data only).

## Dashboard Principles

- **Aggregate Only**: Counts, percentages, distributions
- **No User Tracking**: Never display individual anonymous_ids
- **Operational Focus**: System health, not user behavior
- **Privacy-Preserving**: Metrics cannot correlate across users

## Dashboard Definitions

### System Health Dashboard

**Purpose**: Overall platform health overview

**Metrics**:
- Database health status (healthy/degraded/unhealthy)
- Redis cache hit rate (%)
- Elasticsearch query latency (p99 milliseconds)
- Ollama response time (p99 milliseconds)
- API endpoint latency (p99 milliseconds)
- Error rate (% of requests)

**Privacy**: All metrics are aggregate, no user data

### Database Dashboard

**Purpose**: PostgreSQL database monitoring

**Metrics**:
- Connection pool utilization (%)
- Query latency distribution (p50, p95, p99)
- Active connections count
- Query error rate (%)
- Replication lag (if applicable)

**Privacy**: No individual query tracking, aggregate only

### Cache Dashboard

**Purpose**: Redis cache performance

**Metrics**:
- Cache hit rate (%)
- Cache miss rate (%)
- Memory usage (%)
- Eviction rate (keys/second)
- Connection count

**Privacy**: No cache key inspection, aggregate metrics only

### Search Dashboard

**Purpose**: Elasticsearch search performance

**Metrics**:
- Search query latency (p99 milliseconds)
- Index health status
- Query error rate (%)
- Index size (GB)
- Document count (aggregate)

**Privacy**: No individual search query tracking

### AI Service Dashboard

**Purpose**: Ollama LLM service monitoring

**Metrics**:
- Response time (p99 milliseconds)
- Request rate (requests/second)
- Error rate (%)
- Model loading status
- Token generation rate

**Privacy**: No individual request tracking, aggregate only

### Business Metrics Dashboard

**Purpose**: Platform business metrics (aggregate only)

**Metrics**:
- Anonymous sessions active (count)
- Assessments completed today (count)
- Matches generated last hour (count)
- Checkpoint success rate (%)
- Human review queue depth (count)

**Privacy**: 
- No individual anonymous_ids displayed
- Aggregate counts only
- No user-level tracking

### API Performance Dashboard

**Purpose**: API endpoint performance

**Metrics**:
- Endpoint latency (p99 milliseconds) per endpoint
- Request rate (requests/second) per endpoint
- Error rate (%) per endpoint
- Throughput (requests/second) overall

**Privacy**: No request-level tracking, aggregate per endpoint

## Dashboard Access

- **Operational Team**: Full access to all dashboards
- **Privacy Policy**: All dashboards follow privacy-preserving principles
- **Data Retention**: Metrics retained for operational purposes only

## Implementation Notes

- Dashboards can be implemented using:
  - Grafana (recommended)
  - Prometheus + Grafana
  - Custom dashboard solution
- All metrics must be aggregate-only
- No user-level data visualization
- Privacy-preserving by design

## Alerting

Alerts configured based on health check thresholds:
- Database: Alert on 3 consecutive failures
- High latency: Alert when p99 > 500ms
- Error rate: Alert when error rate > 1%
- Cache: Alert when hit rate < 80%

All alerts are operational (system health), not user-focused.

