#!/bin/bash
# Bash script to start development servers
# Usage: ./scripts/start-dev.sh

echo "Starting AI-Enabled LLC Matching Platform..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.11+"
    exit 1
fi
echo "Python: $(python3 --version)"

# Check if Node is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "Node.js: $(node --version)"

# Start Backend
echo ""
echo "Starting Backend Server (port 8000)..."
cd backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start Frontend
echo "Starting Frontend Server (port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "Servers starting..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Universal Canvas: http://localhost:3000/canvas"
echo ""
echo "Press Ctrl+C to stop all servers."

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

