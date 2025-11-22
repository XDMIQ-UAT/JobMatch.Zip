#!/usr/bin/env python3
"""
State Checkpointer Service
Periodically creates checkpoints of database and cache state.
"""
import os
import time
import subprocess
from datetime import datetime

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "jobmatch")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "jobmatch")
POSTGRES_DB = os.getenv("POSTGRES_DB", "jobmatch")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
CHECKPOINT_INTERVAL = int(os.getenv("CHECKPOINT_INTERVAL", "1800"))  # 30 minutes

def create_checkpoint():
    """Create a checkpoint of all stateful services."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_dir = f"/checkpoints/{timestamp}"
    
    print(f"Creating checkpoint: {timestamp}")
    
    try:
        # Create checkpoint directory
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Backup PostgreSQL
        print("Backing up PostgreSQL...")
        pg_file = f"{checkpoint_dir}/postgres.sql.gz"
        pg_cmd = f"PGPASSWORD={POSTGRES_PASSWORD} pg_dump -h {POSTGRES_HOST} -U {POSTGRES_USER} {POSTGRES_DB} | gzip > {pg_file}"
        subprocess.run(pg_cmd, shell=True, check=True)
        
        # Backup Redis
        print("Backing up Redis...")
        redis_cmd = f"redis-cli -h {REDIS_HOST} --rdb {checkpoint_dir}/redis.rdb"
        subprocess.run(redis_cmd, shell=True, check=True)
        
        # Mark as last known good
        lkg_link = "/checkpoints/last-known-good"
        if os.path.exists(lkg_link):
            os.remove(lkg_link)
        os.symlink(checkpoint_dir, lkg_link)
        
        print(f"Checkpoint created successfully: {timestamp}")
        return True
        
    except Exception as e:
        print(f"Checkpoint failed: {e}")
        return False

def main():
    """Main loop - create checkpoints periodically."""
    print(f"Starting checkpointer service (interval: {CHECKPOINT_INTERVAL}s)")
    
    while True:
        create_checkpoint()
        print(f"Sleeping for {CHECKPOINT_INTERVAL} seconds...")
        time.sleep(CHECKPOINT_INTERVAL)

if __name__ == "__main__":
    main()
