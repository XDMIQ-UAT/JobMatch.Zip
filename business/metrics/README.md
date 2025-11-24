# Metrics - KPIs and OKRs

This folder contains Key Performance Indicators (KPIs) and Objectives and Key Results (OKRs) definitions for the platform.

## Purpose

Define and track business metrics:
- **KPIs**: Key Performance Indicators for platform health and business success
- **OKRs**: Objectives and Key Results for strategic goals
- **Privacy-Preserving**: All metrics are aggregate-only (no individual user tracking)

## Key Principles

- **Aggregate Only**: Counts, percentages, distributions (no user-level data)
- **Anonymous-First**: Metrics don't require identity information
- **Privacy-Preserving**: No correlation across users
- **Business-Focused**: Metrics that matter for platform success

## Files

- `kpis.yaml` - KPI definitions and targets
- `okrs.yaml` - OKR definitions and tracking

## Metric Categories

### Platform Health KPIs
- System uptime
- API latency (p99)
- Error rates
- Component health status

### Business KPIs
- Anonymous sessions active
- Assessments completed
- Matches generated
- Checkpoint success rate
- Human review queue depth

### User Engagement KPIs
- Assessment completion rate
- Match acceptance rate
- Platform return rate
- Feature usage (aggregate)

## Privacy Constraints

- **Never Track**: Individual anonymous_ids in metrics
- **Never Correlate**: Metrics across users
- **Always Aggregate**: Counts, percentages, distributions only
- **No Identity**: Metrics don't require identity information

## Related Documentation

- `health/dashboards.md` - Dashboard configurations
- `docs/SCALING.md` - Scaling metrics
- `docs/GROWTH_STRATEGY.md` - Growth metrics

