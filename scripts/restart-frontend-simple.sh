#!/bin/bash
# Simple script to restart frontend on VM
# Usage: gcloud compute ssh jobmatch-vm --zone=us-central1-a --command="bash -s" < scripts/restart-frontend-simple.sh

cd /opt/jobmatch/frontend || exit 1

echo "Stopping frontend..."
pkill -f "next start" || true
sleep 2

echo "Starting frontend..."
export NODE_ENV=production
export PORT=3000
nohup npm run start > /tmp/frontend.log 2>&1 &
sleep 3

echo "Frontend started. PID:"
ps aux | grep "next start" | grep -v grep | awk '{print $2}'

echo ""
echo "✅ Frontend restarted!"
echo "Logs: tail -f /tmp/frontend.log"

