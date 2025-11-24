#!/bin/bash
# Create systemd service for backend
# Run this on the VM: bash scripts/create-backend-service.sh

cat > /tmp/jobmatch-backend.service << 'EOF'
[Unit]
Description=JobMatch Backend API
After=network.target

[Service]
Type=simple
User=dash
WorkingDirectory=/opt/jobmatch
Environment="PATH=/opt/jobmatch/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/jobmatch/.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --app-dir /opt/jobmatch
Restart=always
RestartSec=10
StandardOutput=append:/home/dash/.logs/jobmatch-backend.log
StandardError=append:/home/dash/.logs/jobmatch-backend.log

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/jobmatch-backend.service /etc/systemd/system/jobmatch-backend.service
sudo systemctl daemon-reload
sudo systemctl enable jobmatch-backend.service
sudo systemctl start jobmatch-backend.service

echo "✅ Backend service created and started"
echo ""
echo "Check status: sudo systemctl status jobmatch-backend"
echo "View logs: tail -f ~/.logs/jobmatch-backend.log"

