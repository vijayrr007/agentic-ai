#!/bin/bash

# Agentic AI Platform - Status Script
# This script checks the status of all services

echo "📊 Agentic AI Platform Status"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check PostgreSQL
echo -n "PostgreSQL:   "
if brew services list | grep -q "postgresql@16.*started"; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Stopped${NC}"
fi

# Check Backend
echo -n "Backend:      "
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC} (PID: $BACKEND_PID, Port: 8000)"
    else
        echo -e "${RED}✗ Stopped${NC} (stale PID file)"
    fi
elif lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC} (Port: 8000)"
else
    echo -e "${RED}✗ Stopped${NC}"
fi

# Check Frontend
echo -n "Frontend:     "
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC} (PID: $FRONTEND_PID, Port: 5173)"
    else
        echo -e "${RED}✗ Stopped${NC} (stale PID file)"
    fi
elif lsof -ti:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC} (Port: 5173)"
else
    echo -e "${RED}✗ Stopped${NC}"
fi

echo ""
echo "URLs:"
echo "  Frontend:  ${BLUE}http://localhost:5173${NC}"
echo "  API:       ${BLUE}http://localhost:8000${NC}"
echo "  API Docs:  ${BLUE}http://localhost:8000/api/v1/docs${NC}"
echo ""

# Check if logs exist and show recent entries
if [ -f "logs/backend.log" ]; then
    echo "Recent Backend Logs:"
    tail -n 3 logs/backend.log
    echo ""
fi

if [ -f "logs/frontend.log" ]; then
    echo "Recent Frontend Logs:"
    tail -n 3 logs/frontend.log
    echo ""
fi

