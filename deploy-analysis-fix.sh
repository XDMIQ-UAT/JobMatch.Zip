#!/bin/bash
# Deploy JobMatch Analysis Fix to VM

echo "🚀 Deploying JobMatch Analysis Fix..."
echo ""

# SSH into VM and deploy
gcloud compute ssh futurelink-vm --zone=us-central1-a --command "
  echo '📥 Pulling latest changes...'
  cd ~/jobmatch-ai
  git pull origin master
  
  echo '🔨 Building backend...'
  cd backend
  npm run build
  
  echo '🔄 Restarting backend service...'
  pm2 restart backend
  
  echo '✅ Deployment complete!'
  echo ''
  echo '📊 Backend status:'
  pm2 status backend
  
  echo ''
  echo '📝 Recent logs:'
  pm2 logs backend --lines 20 --nostream
"

echo ""
echo "✅ Fix deployed successfully!"
echo ""
echo "To test the fix:"
echo "1. Open Chrome and go to LinkedIn"
echo "2. Navigate to a job posting"
echo "3. Click the JobMatch AI extension icon"
echo "4. The job analysis should now work correctly"
echo ""
echo "To monitor logs in real-time:"
echo "gcloud compute ssh futurelink-vm --zone=us-central1-a --command 'pm2 logs backend'"

