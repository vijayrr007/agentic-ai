#!/bin/bash

# Agentic AI Platform - Stop Script
# This script stops both backend and frontend servers

echo "🛑 Stopping Agentic AI Platform..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Stop Backend
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm logs/backend.pid
        echo -e "${GREEN}✓ Backend stopped${NC}"
    else
        echo "Backend is not running"
        rm logs/backend.pid
    fi
else
    echo "No backend PID file found"
fi
echo ""

# Stop Frontend
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm logs/frontend.pid
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    else
        echo "Frontend is not running"
        rm logs/frontend.pid
    fi
else
    echo "No frontend PID file found"
fi
echo ""

# Kill any remaining processes on the ports (backup cleanup)
echo "Cleaning up any remaining processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

echo -e "${GREEN}✓ Platform stopped${NC}"
echo ""

