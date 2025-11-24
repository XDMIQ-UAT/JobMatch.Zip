# Identity Proxy - Anonymous Session Flows

This folder contains configurations for anonymous session management and voluntary identification flows.

## Purpose

Manage anonymous-first identity architecture:
- **Anonymous Sessions**: Zero-knowledge session management
- **Voluntary Identification**: Opt-in identity linking (never required)
- **Multiple Personas**: Support for multiple anonymous profiles per user
- **Identity Policies**: Rules for anonymous-first operations

## Key Principles

- **Zero-Knowledge**: Platform cannot reverse-engineer identity from anonymous_id
- **Anonymous-First**: All features work without identity
- **Voluntary Identification**: User opts in, never required
- **Multiple Personas**: Users can create multiple anonymous profiles

## Files

- `policies/anonymous-sessions.yaml` - Anonymous session management policies
- `flows.yaml` - Session flow definitions

## Architecture

### Anonymous Session Creation
1. User visits site → Generate anonymous_id → Create session
2. Session data keyed by anonymous_id only
3. No identity information stored

### Voluntary Identification Flow
1. User explicitly opts in (with clear consent UI)
2. Identity stored in separate table (not linked to anonymous_id in main tables)
3. User can delete identity link at any time
4. Platform cannot correlate anonymous_id → real identity without explicit user action

## Related Code

- `backend/auth/anonymous_identity.py` - Anonymous identity manager
- `backend/api/auth.py` - Authentication endpoints

## Constraints

- Platform CANNOT reverse-engineer identity from anonymous_id
- Sessions MUST work without any identity information
- Voluntary identification MUST be opt-in, never required
- Identity linking MUST be user-initiated with clear consent UI
- User MUST be able to delete identity link at any time

