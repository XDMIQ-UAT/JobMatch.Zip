# Privacy Policy

## Overview

This privacy policy defines how the AI-Enabled LLC Matching Platform handles user data, with a focus on anonymous-first operations and zero-knowledge architecture.

## Core Principles

### Anonymous-First Architecture
- **Default Anonymous**: All platform features work without identity
- **Zero-Knowledge**: Platform cannot reverse-engineer identity from anonymous IDs
- **Voluntary Identification**: Identity linking is opt-in only, never required

### Data Minimization
- **Minimal Data Collection**: Only collect data necessary for platform functionality
- **No Identity Required**: Core features work without identity information
- **Aggregate Metrics**: Metrics are aggregate-only (no individual tracking)

### User Control
- **User Ownership**: Users control their data and identity linking
- **Deletion Rights**: Users can delete identity links at any time
- **Multiple Personas**: Users can create multiple anonymous profiles

## Data Handling

### Anonymous Session Data

**What We Store**:
- Anonymous ID (cryptographically secure hash)
- Session metadata (no identity information)
- Assessment results (keyed by anonymous ID)
- Capability scores (keyed by anonymous ID)
- Match preferences (keyed by anonymous ID)

**What We Don't Store**:
- Real identity information (unless voluntarily provided)
- Email addresses (unless voluntarily provided)
- Phone numbers (unless voluntarily provided)
- Social media account links (unless voluntarily provided)

**Storage Duration**: Anonymous session data retained for platform functionality
**Deletion**: Users can request deletion of anonymous session data

### Voluntary Identity Data

**What We Store** (only if user opts in):
- Identity information in separate table
- Encrypted identity data
- Consent timestamp
- User-controlled mapping

**Storage Duration**: Until user requests deletion
**Deletion**: Users can delete identity link at any time
**Correlation**: Platform cannot correlate anonymous ID → identity without user action

### Assessment Data

**What We Store**:
- XDMIQ assessment answers (keyed by anonymous ID)
- Capability scores (keyed by anonymous ID)
- Portfolio data (if provided, keyed by anonymous ID)

**What We Don't Store**:
- Identity information linked to assessments
- Personal information in assessment data

**Usage**: Used for matching algorithm and capability assessment
**Privacy**: Assessment data cannot be linked to identity without user action

### Matching Data

**What We Store**:
- Match results (keyed by anonymous ID)
- Match preferences (keyed by anonymous ID)
- Match acceptance status (keyed by anonymous ID)

**What We Don't Store**:
- Identity information linked to matches
- Employer identity (unless voluntarily provided)

**Usage**: Used to improve matching algorithm
**Privacy**: Match data cannot be linked to identity without user action

## Data Processing

### Allowed Processing
- Capability assessment scoring
- Matching algorithm execution
- Aggregate metric calculation
- Platform health monitoring

### Prohibited Processing
- Identity correlation without user consent
- Cross-user data correlation
- Individual user tracking
- Identity reverse-engineering

## Data Sharing

### Internal Use
- Data used only for platform functionality
- No sharing with third parties without user consent
- Aggregate metrics only (no individual data)

### Third-Party Services
- Third-party services used only for platform functionality
- No identity data shared unless user explicitly consents
- Anonymous data sharing only when necessary for platform function

## User Rights

### Right to Anonymity
- Users can use platform completely anonymously
- No identity required for core features
- Anonymous-first by default

### Right to Identity Control
- Users control identity linking (opt-in)
- Users can delete identity links at any time
- Users can create multiple anonymous personas

### Right to Data Deletion
- Users can request deletion of identity links
- Users can request deletion of anonymous session data
- Deletion requests processed within 30 days

### Right to Transparency
- Users can see what data is stored
- Users can see how data is used
- Privacy policy clearly communicated

## Security Measures

### Data Protection
- Anonymous IDs: Cryptographically secure (SHA256)
- Identity data: Encrypted storage
- Session data: Secure storage
- API: HTTPS only
- IP addresses: Hashed (SHA256) for security validation, never stored in raw form

### IP Address Handling
- **Purpose**: Security validation (preventing magic link abuse, fraud detection)
- **Storage**: Only hashed IP addresses (SHA256 with salt) are stored temporarily
- **Retention**: Hashed IPs deleted immediately after magic link verification (max 24 hours)
- **Privacy**: Raw IP addresses are never stored or logged
- **Zero-Knowledge**: Hashed IPs cannot be reverse-engineered to identify users
- **Compliance**: This approach maintains zero-knowledge principles while enabling security

### Access Control
- Platform access: Anonymous-first
- Identity access: User-controlled
- Administrative access: Restricted and audited

## Compliance

### Privacy Regulations
- GDPR compliance (if applicable)
- CCPA compliance (if applicable)
- Anonymous-first architecture supports compliance

### Data Retention
- Anonymous session data: Retained for platform functionality
- Identity data: Retained until user deletion request
- Aggregate metrics: Retained for operational purposes

## Policy Updates

### Notification
- Users notified of significant policy changes
- Policy version tracked
- Changes documented

### Effective Date
- Policy effective from platform launch
- Updates effective 30 days after notification

## Contact

For privacy questions or data deletion requests:
- Platform: Use platform contact mechanism
- Privacy concerns: Documented in platform

## Related Policies

- `data-boundaries.md` - Data boundary definitions
- `identity-proxy/policies/anonymous-sessions.yaml` - Session policies

