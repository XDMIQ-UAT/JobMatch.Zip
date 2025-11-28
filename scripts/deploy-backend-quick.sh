#!/bin/bash
# Quick backend deployment fix for jobmatch-vm

set -e

echo "🚀 Deploying backend to jobmatch-vm..."

cd /opt/jobmatch

# Backup .env
cp .env /tmp/.env.backup 2>/dev/null || echo "No .env to backup"

# Extract new backend
echo "📦 Extracting backend..."
cd /opt/jobmatch
unzip -o /tmp/backend-deploy.zip -d .

# Restore .env
cp /tmp/.env.backup .env 2>/dev/null || echo "No .env backup found"

# Fix permissions
chown -R dash:dash /opt/jobmatch/backend

# Install dependencies
echo "📥 Installing dependencies..."
pip3 install -q stripe pydantic fastapi uvicorn python-dotenv

# Kill any existing backend
pkill -f "uvicorn backend.main" || true
sleep 2

# Start backend
echo "▶️  Starting backend..."
cd /opt/jobmatch
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &

sleep 5

# Check if running
if pgrep -f "uvicorn backend.main" > /dev/null; then
    echo "✅ Backend started successfully"
    ps aux | grep "uvicorn backend.main" | grep -v grep
else
    echo "❌ Backend failed to start"
    echo "Last 20 lines of log:"
    tail -20 /tmp/backend.log
    exit 1
fi
