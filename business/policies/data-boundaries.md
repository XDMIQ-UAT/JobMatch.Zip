# Data Boundaries

## Overview

This document defines data boundaries for the AI-Enabled LLC Matching Platform: what data can be stored, what cannot be stored, and processing limitations.

## Core Boundaries

### Anonymous-First Boundary
**Principle**: All platform features work with anonymous data only

**Allowed**:
- Anonymous IDs (cryptographically secure)
- Session data (no identity)
- Assessment results (keyed by anonymous ID)
- Capability scores (keyed by anonymous ID)
- Match preferences (keyed by anonymous ID)

**Prohibited**:
- Identity information in core platform tables
- Correlation between anonymous IDs and identity (without user action)
- Identity requirements for core features

### Zero-Knowledge Boundary
**Principle**: Platform cannot reverse-engineer identity from anonymous IDs

**Allowed**:
- Anonymous ID generation (SHA256 hash)
- Session data keyed by anonymous ID
- Assessment data keyed by anonymous ID

**Prohibited**:
- Identity information in anonymous session tables
- Correlation mechanisms without user consent
- Identity reverse-engineering attempts

### Voluntary Identification Boundary
**Principle**: Identity linking is separate, opt-in, user-controlled

**Allowed**:
- Identity data in separate table (if user opts in)
- User-controlled identity mapping
- Encrypted identity storage

**Prohibited**:
- Required identity for core features
- Automatic identity correlation
- Identity linking without explicit consent

## Data Storage Boundaries

### Can Be Stored

#### Anonymous Session Data
- Anonymous ID (primary key)
- Session creation timestamp
- Session metadata (no identity)
- Platform preferences (keyed by anonymous ID)

#### Assessment Data
- XDMIQ answers (keyed by anonymous ID)
- Capability scores (keyed by anonymous ID)
- Portfolio data (if provided, keyed by anonymous ID)
- Assessment timestamps

#### Matching Data
- Match results (keyed by anonymous ID)
- Match preferences (keyed by anonymous ID)
- Match acceptance status (keyed by anonymous ID)

#### Aggregate Metrics
- Counts (anonymous sessions, assessments, matches)
- Percentages (completion rates, acceptance rates)
- Distributions (latency, scores)
- System metrics (uptime, performance)

### Cannot Be Stored

#### Identity Information (in core tables)
- Real names
- Email addresses (unless voluntarily provided)
- Phone numbers (unless voluntarily provided)
- Social media account links (unless voluntarily provided)
- Physical addresses
- Government IDs
- Raw IP addresses (only hashed IPs stored temporarily for security)

#### Correlation Data
- Anonymous ID → Identity mapping (without user consent)
- Cross-user correlation data
- Identity inference data

#### Individual Tracking Data
- Individual user behavior tracking
- User-level analytics
- Individual session tracking (beyond aggregate)

## Data Processing Boundaries

### Allowed Processing

#### Capability Assessment
- XDMIQ scoring (preference-based)
- Capability score calculation
- Portfolio analysis (if provided)
- Matching algorithm execution

#### Platform Operations
- Aggregate metric calculation
- System health monitoring
- Performance optimization
- Matching algorithm improvement

#### User Features
- Anonymous session management
- Assessment flow execution
- Match generation
- Notification delivery (if user opts in)

### Prohibited Processing

#### Identity Correlation
- Reverse-engineering identity from anonymous ID
- Correlating anonymous IDs without user action
- Identity inference from behavior

#### Individual Tracking
- Individual user behavior tracking
- User-level analytics
- Cross-user correlation

#### Data Mining
- Identity mining from anonymous data
- Pattern recognition for identity inference
- Behavioral profiling for identity correlation

## Data Sharing Boundaries

### Internal Sharing

**Allowed**:
- Data sharing within platform for functionality
- Aggregate metrics for operations
- System health data for monitoring

**Prohibited**:
- Identity data sharing (unless user consents)
- Individual user data sharing
- Cross-user correlation sharing

### External Sharing

**Allowed**:
- Aggregate metrics (no individual data)
- Anonymized data for platform functionality
- Third-party services (anonymous data only, if necessary)

**Prohibited**:
- Identity data sharing without user consent
- Individual user data sharing
- Anonymous ID → Identity correlation sharing

## Data Retention Boundaries

### Retention Periods

#### Anonymous Session Data
- **Retention**: For platform functionality
- **Deletion**: User can request deletion
- **Boundary**: No identity correlation

#### Identity Data (if voluntarily provided)
- **Retention**: Until user deletion request
- **Deletion**: User can delete at any time
- **Boundary**: Separate from anonymous data

#### Aggregate Metrics
- **Retention**: For operational purposes (90 days typical)
- **Deletion**: Automatic after retention period
- **Boundary**: Aggregate only, no individual data

### Deletion Boundaries

#### User-Initiated Deletion
- Users can delete identity links
- Users can request anonymous session deletion
- Deletion requests processed within 30 days

#### Automatic Deletion
- Aggregate metrics deleted after retention period
- Expired sessions cleaned up automatically
- No identity data in automatic deletion (separate process)

## Boundary Enforcement

### Technical Enforcement
- Database schema enforces separation (anonymous vs identity tables)
- API endpoints enforce anonymous-first
- Code reviews check boundary compliance

### Policy Enforcement
- Privacy policy defines boundaries
- Data boundary documentation
- Regular audits of boundary compliance

### Monitoring
- Boundary violations detected and alerted
- Regular boundary compliance reviews
- Privacy-preserving monitoring only

## Related Policies

- `privacy.md` - Privacy policy
- `identity-proxy/policies/anonymous-sessions.yaml` - Session policies
- `docs/SECURITY_RISKS.md` - Security considerations

