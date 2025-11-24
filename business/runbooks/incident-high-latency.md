# Incident: High API Latency (>500ms p99)

## Overview

**Severity**: High  
**Impact**: User experience degraded, matching queue backing up  
**Detection**: Automated monitoring alerts when p99 latency exceeds 500ms

## Symptoms

- API response times exceed 500ms (p99)
- User experience degraded (slow page loads, timeouts)
- Matching queue backing up (jobs not processing)
- Increased error rates (timeout errors)
- User complaints about slow performance

## Diagnosis

### Step 1: Check Elasticsearch Health
```bash
# Check Elasticsearch cluster health
curl http://localhost:9200/_cluster/health

# Check search query performance
curl http://localhost:9200/_nodes/stats
```

**Expected**: Cluster status green, query latency < 100ms  
**Issue**: Cluster yellow/red, high query latency

### Step 2: Check Redis Cache Hit Rate
```bash
# Check Redis cache statistics
redis-cli INFO stats

# Check cache hit rate
redis-cli INFO stats | grep keyspace
```

**Expected**: Cache hit rate > 80%  
**Issue**: Low cache hit rate (< 60%), high miss rate

### Step 3: Check Database Query Performance
```bash
# Check database connection pool
# Review slow query log
# Check active connections

# Query database metrics
SELECT * FROM pg_stat_activity;
```

**Expected**: Query latency < 50ms (p99), connection pool < 80% utilized  
**Issue**: High query latency, connection pool exhaustion

### Step 4: Check Ollama Response Times
```bash
# Check Ollama service health
curl http://localhost:11434/api/tags

# Monitor response times
# Check Ollama logs for slow responses
```

**Expected**: Ollama response time < 200ms (p99)  
**Issue**: High Ollama latency (> 500ms)

### Step 5: Check API Endpoint Performance
```bash
# Review API logs for slow endpoints
# Check endpoint-specific latency

# Identify slowest endpoints
curl http://localhost:8000/metrics
```

**Expected**: All endpoints < 300ms (p99)  
**Issue**: Specific endpoints causing high latency

## Resolution

### Immediate Actions

1. **Scale Elasticsearch Nodes** (if Elasticsearch is bottleneck)
   ```bash
   # Scale Elasticsearch cluster
   kubectl scale deployment elasticsearch --replicas=3
   # Or add nodes to Elasticsearch cluster
   ```

2. **Increase Redis Cache Size** (if cache hit rate low)
   ```bash
   # Increase Redis memory limit
   # Restart Redis with larger memory allocation
   # Or scale Redis cluster
   ```

3. **Add Database Read Replicas** (if database is bottleneck)
   ```bash
   # Add read replicas to PostgreSQL
   # Route read queries to replicas
   # Scale connection pool if needed
   ```

4. **Optimize Ollama Batch Size** (if Ollama is bottleneck)
   ```bash
   # Reduce batch size for Ollama requests
   # Add Ollama instances for load balancing
   # Check model loading status
   ```

5. **Scale API Instances** (if API is bottleneck)
   ```bash
   # Scale API deployment
   kubectl scale deployment backend-api --replicas=5
   # Or add more API instances
   ```

### Step-by-Step Resolution

1. **Identify Root Cause**
   - Review monitoring dashboards
   - Check health check results
   - Identify slowest component

2. **Apply Fix**
   - Follow component-specific resolution above
   - Monitor metrics during fix application

3. **Verify Resolution**
   - Check p99 latency returns to < 300ms
   - Verify matching queue processing normally
   - Confirm error rates return to baseline

4. **Create Checkpoint** (if state changed)
   ```bash
   # Create checkpoint before any state changes
   curl -X POST http://localhost:8000/api/checkpoints/create \
     -H "Content-Type: application/json" \
     -d '{"tag": "pre-scaling-fix"}'
   ```

## Prevention

### Monitoring
- Monitor p99 latency continuously
- Alert at 300ms threshold (before user impact)
- Auto-scale triggers at 400ms (proactive scaling)

### Proactive Measures
- Regular capacity planning
- Load testing before traffic spikes
- Database query optimization
- Cache warming strategies
- Ollama batch size tuning

### Runbook Updates
- Document any new root causes discovered
- Update resolution steps based on learnings
- Add prevention measures as identified

## Related Runbooks

- `scaling-database.md` - Database scaling procedures
- `scaling-elasticsearch.md` - Elasticsearch scaling
- `optimization-cache.md` - Cache optimization

## Escalation

If resolution steps don't resolve issue within 30 minutes:
1. Escalate to senior engineer
2. Consider rolling back recent deployments
3. Check for external dependencies (third-party APIs)
4. Review recent code changes that might affect performance

## Post-Incident

After resolution:
1. Document root cause analysis
2. Update monitoring thresholds if needed
3. Review prevention measures
4. Update this runbook with learnings

