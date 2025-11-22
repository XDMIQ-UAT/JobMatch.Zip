#!/bin/bash
# Deploy backend to VM using git

echo "🚀 Deploying JobMatch AI Backend..."

# Navigate to the jobmatch-ai directory
cd ~/jobmatch-ai || exit 1

# Pull latest changes from GitHub
echo "📥 Pulling latest changes from GitHub..."
git pull origin master

# Navigate to backend directory
cd backend || exit 1

# Install dependencies if needed
echo "📦 Installing dependencies..."
npm install

# Build the project
echo "🔨 Building TypeScript..."
npm run build

# Restart PM2 service
echo "🔄 Restarting PM2 service..."
pm2 restart jobmatch-backend

# Show status
echo "✅ Deployment complete!"
pm2 status