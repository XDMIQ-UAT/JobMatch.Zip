#!/bin/bash
# Simple backend startup script

cd /opt/jobmatch || exit 1

# Kill any existing backend
pkill -f "uvicorn backend.main:app" || true
sleep 2

# Start backend
source .venv/bin/activate
export PYTHONPATH=/opt/jobmatch
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > ~/.logs/jobmatch-backend.log 2>&1 &

sleep 5

# Check if started
if ps aux | grep -E "[u]vicorn backend.main:app" > /dev/null; then
    echo "✅ Backend started successfully"
    ps aux | grep -E "[u]vicorn backend.main:app" | grep -v grep
    echo ""
    echo "Logs: tail -f ~/.logs/jobmatch-backend.log"
else
    echo "❌ Backend failed to start"
    echo ""
    echo "Recent logs:"
    tail -20 ~/.logs/jobmatch-backend.log 2>/dev/null || echo "No logs found"
    exit 1
fi

