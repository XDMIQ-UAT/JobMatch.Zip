#!/bin/bash
# Run data generation script overnight on VM
# This script can be run as a background job

set -e

VM_NAME="${VM_NAME:-jobmatch-vm}"
ZONE="${GCP_ZONE:-us-central1-a}"
MAX_JOBS="${MAX_JOBS:-50}"
MAX_CANDIDATES="${MAX_CANDIDATES:-100}"
LOG_FILE="/tmp/overnight-data-generation.log"

echo "🌙 Starting overnight data generation..."
echo "   Max Jobs: $MAX_JOBS"
echo "   Max Candidates: $MAX_CANDIDATES"
echo "   Log file: $LOG_FILE"
echo ""

# Upload script to VM
echo "📤 Uploading data generation script..."
gcloud compute scp scripts/generate-test-data.py $VM_NAME:/opt/jobmatch/scripts/ --zone=$ZONE

# Run script in background with nohup
echo "🚀 Starting data generation in background..."
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    cd /opt/jobmatch
    export DATABASE_URL='postgresql://jobfinder:jobfinder@postgres:5432/jobfinder'
    export OLLAMA_BASE_URL='http://localhost:11434'
    export OLLAMA_MODEL='llama3.2'
    export MAX_JOBS=$MAX_JOBS
    export MAX_CANDIDATES=$MAX_CANDIDATES
    
    # Install Python dependencies if needed
    python3 -m pip install requests sqlalchemy psycopg2-binary --quiet || true
    
    # Run in background with logging
    nohup python3 scripts/generate-test-data.py > $LOG_FILE 2>&1 &
    
    echo '✅ Data generation started in background'
    echo '   Process ID: '$(jobs -p)
    echo '   Log file: $LOG_FILE'
    echo ''
    echo 'To check progress:'
    echo '   tail -f $LOG_FILE'
    echo ''
    echo 'To check if still running:'
    echo '   ps aux | grep generate-test-data'
"

echo ""
echo "✅ Overnight data generation started!"
echo ""
echo "📋 To check progress, run:"
echo "   gcloud compute ssh $VM_NAME --zone=$ZONE --command='tail -f $LOG_FILE'"
echo ""
echo "📊 To check current database stats:"
echo "   gcloud compute ssh $VM_NAME --zone=$ZONE --command='docker-compose exec -T postgres psql -U jobfinder -d jobfinder -c \"SELECT COUNT(*) FROM job_postings; SELECT COUNT(*) FROM anonymous_users;\"'"

