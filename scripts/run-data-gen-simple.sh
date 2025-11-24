#!/bin/bash
# Simple script to run data generation in Docker container
# Usage: Upload this to VM and run it

cd /opt/jobmatch

MAX_JOBS=${1:-2}
MAX_CANDIDATES=${2:-3}
LOG_FILE="/tmp/overnight-data-generation.log"

echo "🌙 Starting data generation..."
echo "   Max Jobs: $MAX_JOBS"
echo "   Max Candidates: $MAX_CANDIDATES"
echo "   Log file: $LOG_FILE"
echo ""

# Run in Docker container
docker compose exec -d app bash -c "
export DATABASE_URL='postgresql://jobfinder:jobfinder@postgres:5432/jobfinder'
export OLLAMA_BASE_URL='http://ollama:11434'
export OLLAMA_MODEL='llama3.2'
export MAX_JOBS=$MAX_JOBS
export MAX_CANDIDATES=$MAX_CANDIDATES
python3 scripts/generate-test-data.py > $LOG_FILE 2>&1
"

sleep 2

echo "✅ Data generation started in background"
echo "   Log file: $LOG_FILE"
echo ""
echo "To check progress:"
echo "   tail -f $LOG_FILE"
echo ""
echo "To check if still running:"
echo "   docker compose exec app ps aux | grep generate-test-data"

