# Checkpoint Workflows Prompt Template

## Context

Creating state checkpoints and last-known-good (LKG) recovery workflows.

## Pattern

Reference: `backend/resilience/state_management.py`, `scripts/checkpoint.ps1`, `scripts/recover.ps1`

## Checkpoint Creation

```python
def create_checkpoint(tag: str = None):
    """
    Create system state checkpoint.
    
    Steps:
    1. Dump PostgreSQL database (pg_dump)
    2. Save Redis data (RDB snapshot)
    3. Snapshot Elasticsearch indices
    4. Bundle into timestamped archive
    5. Store in checkpoints_data volume
    6. Update last-known-good if tag="last-known-good"
    """
    checkpoint_id = f"checkpoint_{datetime.utcnow().isoformat()}"
    
    # Database checkpoint
    subprocess.run(["pg_dump", ...])
    
    # Redis checkpoint
    subprocess.run(["redis-cli", "BGSAVE"])
    
    # Elasticsearch snapshot
    # ... snapshot API call
    
    # Bundle
    tar.create(checkpoint_id, [db_dump, redis_rdb, es_snapshot])
    
    return checkpoint_id
```

## Recovery Workflow

```python
def restore_checkpoint(checkpoint_id: str):
    """
    Restore system to checkpoint state.
    
    Steps:
    1. Stop services (graceful drain)
    2. Extract checkpoint archive
    3. Restore PostgreSQL (pg_restore)
    4. Restore Redis (load RDB)
    5. Restore Elasticsearch (restore snapshot)
    6. Restart services
    7. Verify health
    """
    # Stop services
    docker_compose_down()
    
    # Restore data
    pg_restore(...)
    redis_load_rdb(...)
    es_restore_snapshot(...)
    
    # Restart
    docker_compose_up()
    
    # Verify
    assert health_check() == "healthy"
```

## Last-Known-Good Pattern

```python
def mark_last_known_good(checkpoint_id: str):
    """Mark checkpoint as last-known-good."""
    # Create symlink or tag
    lkg_path = "checkpoints_data/last-known-good"
    os.symlink(checkpoint_id, lkg_path)

def restore_last_known_good():
    """Restore to last-known-good checkpoint."""
    lkg_id = os.readlink("checkpoints_data/last-known-good")
    restore_checkpoint(lkg_id)
```

## Scheduled Checkpoints

```python
# In state-checkpointer container
def scheduled_checkpoint():
    """Run every 30 minutes."""
    checkpoint_id = create_checkpoint()
    
    # If successful, update LKG
    if verify_checkpoint(checkpoint_id):
        mark_last_known_good(checkpoint_id)
```

## Constraints

- MUST create checkpoint before state-changing operations
- MUST support rollback to any checkpoint
- MUST preserve data integrity during restore
- MUST verify health after restore

## Integration Points

- Assessment creation → checkpoint before storage
- Matching algorithm update → checkpoint before deploy
- Database migrations → checkpoint before migration
- System reboot → restore LKG on failure

