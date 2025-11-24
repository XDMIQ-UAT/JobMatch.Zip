# Identity Proxy Prompt Template

## Context

Managing anonymous sessions and voluntary identification flows. Zero-knowledge architecture.

## Pattern

Reference: `backend/auth/anonymous_identity.py`, `business/identity-proxy/flows.yaml`

## Architecture Principles

1. **Zero-Knowledge**: Platform cannot link anonymous_id to real identity
2. **Anonymous-First**: All features work without identity
3. **Voluntary Identification**: User opts in, never required
4. **Multiple Personas**: User can create multiple anonymous profiles

## Flow: Anonymous Session Creation

```python
def create_anonymous_session():
    """
    1. Generate cryptographically secure anonymous_id
    2. Create session keyed by anonymous_id
    3. Store session data (no identity information)
    4. Return anonymous_id to client
    """
    anonymous_id = secrets.token_bytes(32)
    session = {
        "anonymous_id": anonymous_id,
        "created_at": datetime.utcnow(),
        "metadata": {}  # No identity data
    }
    return anonymous_id
```

## Flow: Voluntary Identification

```python
def link_identity(anonymous_id: str, identity_data: dict, consent: bool):
    """
    User-initiated identity linking.
    
    Steps:
    1. Verify user consent (explicit opt-in)
    2. Store identity in separate table (not linked to anonymous_id in main tables)
    3. Create mapping table (user-controlled, can be deleted)
    4. Platform cannot reverse-engineer identity from anonymous_id
    """
    if not consent:
        raise ValueError("Identity linking requires explicit consent")
    
    # Store in separate identity table
    identity_record = {
        "anonymous_id": anonymous_id,
        "identity_data": identity_data,
        "consented_at": datetime.utcnow(),
        "user_can_delete": True
    }
```

## Constraints

- Platform CANNOT reverse-engineer identity from anonymous_id
- Sessions MUST work without any identity information
- Voluntary identification MUST be opt-in, never required
- Identity linking MUST be user-initiated with clear consent UI
- User MUST be able to delete identity link at any time

## Storage Structure

```
anonymous_sessions/
  - anonymous_id (primary key)
  - session_data (no identity)
  - created_at

identity_links/ (separate table)
  - anonymous_id (foreign key)
  - identity_data (encrypted)
  - consented_at
  - user_can_delete (boolean)
```

## Integration Points

- All assessments keyed by anonymous_id
- All matches displayed to anonymous_id
- Identity only used if user explicitly opts in
- Personalization features check for voluntary identity link

