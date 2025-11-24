#!/bin/bash
# Restart Frontend Production Server
# Usage: ./scripts/restart-frontend.sh

echo "Restarting Frontend Production Server..."

# Check if supervisord is available
if command -v supervisorctl &> /dev/null; then
    echo ""
    echo "Restarting via supervisord..."
    sudo supervisorctl restart frontend
    if [ $? -eq 0 ]; then
        echo "✅ Frontend restarted successfully"
        echo ""
        echo "Checking status..."
        sudo supervisorctl status frontend
        exit 0
    else
        echo "❌ Failed to restart frontend via supervisord"
        echo "   Trying manual restart..."
    fi
fi

# Manual restart
cd frontend || exit 1

# Verify build exists
if [ ! -d ".next" ]; then
    echo "❌ Error: Build not found. Run 'npm run build' first."
    exit 1
fi

# Find and kill existing Next.js processes
echo "Stopping existing processes..."
pkill -f "next start" || true
sleep 2

# Start production server
echo "Starting Frontend Production Server..."
export NODE_ENV=production
export PORT=3000
nohup npm run start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✅ Frontend production server started (PID: $FRONTEND_PID)"
echo "   URL: http://localhost:3000"
echo "   Logs: logs/frontend.log"

cd ..

