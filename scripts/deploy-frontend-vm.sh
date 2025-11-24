#!/bin/bash
set -e

echo "Stopping frontend service..."
sudo supervisorctl stop frontend 2>/dev/null || sudo systemctl stop frontend 2>/dev/null || sudo pkill -f 'next start' || true

echo "Extracting new frontend files..."
sudo unzip -o /tmp/frontend-deploy.zip -d /opt/jobmatch/frontend

echo "Cleaning up..."
sudo rm -f /tmp/frontend-deploy.zip

echo "Setting permissions..."
sudo chown -R $(whoami):$(whoami) /opt/jobmatch/frontend 2>/dev/null || true

echo "Restarting frontend service..."
sudo supervisorctl restart frontend 2>/dev/null || sudo systemctl restart frontend 2>/dev/null || (cd /opt/jobmatch/frontend && NODE_ENV=production PORT=3000 nohup npm run start > /tmp/frontend.log 2>&1 &)

echo "Waiting for service to start..."
sleep 5

sudo supervisorctl status frontend 2>/dev/null || sudo systemctl status frontend 2>/dev/null || echo 'Service started in background'

echo "✅ Frontend deployment complete!"
