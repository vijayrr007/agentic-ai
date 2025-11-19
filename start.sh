#!/bin/bash

# Agentic AI Platform - Start Script
# This script starts both backend and frontend servers

set -e

echo "🚀 Starting Agentic AI Platform..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if PostgreSQL is running
echo "📊 Checking PostgreSQL..."
if ! brew services list | grep -q "postgresql@16.*started"; then
    echo -e "${BLUE}Starting PostgreSQL...${NC}"
    brew services start postgresql@16
    sleep 2
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"
echo ""

# Start Backend
echo "🔧 Starting Backend (FastAPI)..."
cd "$SCRIPT_DIR/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo "Please run setup first:"
    echo "  cd backend"
    echo "  python3.12 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Start backend in background
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/api/v1/docs"
echo "  - Logs: logs/backend.log"
echo ""

# Start Frontend
echo "🎨 Starting Frontend (React + Vite)..."
cd "$SCRIPT_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${RED}Error: node_modules not found!${NC}"
    echo "Please run setup first:"
    echo "  cd frontend"
    echo "  npm install"
    exit 1
fi

# Start frontend in background
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "  - App: http://localhost:5173"
echo "  - Logs: logs/frontend.log"
echo ""

echo -e "${GREEN}✨ Platform is starting up!${NC}"
echo ""
echo "Wait a few seconds, then open: ${BLUE}http://localhost:5173${NC}"
echo ""
echo "To view logs in real-time:"
echo "  Backend:  tail -f logs/backend.log"
echo "  Frontend: tail -f logs/frontend.log"
echo ""
echo "To stop the platform:"
echo "  ./stop.sh"
echo ""

