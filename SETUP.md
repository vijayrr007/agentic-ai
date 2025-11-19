# Quick Setup Guide

This guide will help you get the Agentic AI Platform up and running in minutes.

## Prerequisites Check

Run these commands to verify you have the required tools:

```bash
python3 --version  # Should be 3.14+
node --version     # Should be 24+
npm --version      # Should be 11+
psql --version     # Should be 16+ (if not installed, see below)
```

## Step-by-Step Setup

### 1. Install PostgreSQL (if not already installed)

```bash
brew install postgresql@16
brew services start postgresql@16
```

Verify it's running:
```bash
brew services list | grep postgresql
```

### 2. Create Database

```bash
createdb agentic_ai
```

Verify database was created:
```bash
psql -l | grep agentic_ai
```

### 3. Set Up Backend

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (this may take a few minutes)
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database (create tables)
alembic upgrade head
```

### 4. Set Up Frontend

```bash
cd ../frontend

# Install dependencies (this may take a few minutes)
npm install

# Copy environment file
cp .env.example .env
```

### 5. Start the Application

Open two terminal windows/tabs:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 6. Access the Platform

Open your browser and navigate to:
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/api/v1/docs
- **API Health Check**: http://localhost:8000/api/health

## Troubleshooting

### PostgreSQL Connection Error

If you see `could not connect to server`:

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# If not running, start it
brew services start postgresql@16

# Check the database exists
psql -l | grep agentic_ai
```

### Database Migration Error

If `alembic upgrade head` fails:

```bash
# Check database URL in backend/.env
cat backend/.env | grep DATABASE_URL

# Should be: DATABASE_URL=postgresql://localhost/agentic_ai

# Try creating the database again
dropdb agentic_ai  # Warning: This deletes all data!
createdb agentic_ai
alembic upgrade head
```

### Port Already in Use

If you see `Address already in use`:

**For Backend (port 8000):**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

**For Frontend (port 5173):**
```bash
# Find and kill the process
lsof -ti:5173 | xargs kill -9

# Or use a different port
npm run dev -- --port 3000
```

### Module Not Found Errors

If you see import errors:

**Backend:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. **Create Your First Workspace**
   - Navigate to "Settings" in the UI
   - Create a new workspace

2. **Create Your First Agent**
   - Go to "Agents" → "Create Agent"
   - Try the Visual Builder first
   - Give it a name and select some tools
   - Save and run it

3. **Explore the Marketplace**
   - Check out pre-built templates
   - Clone a template to your workspace
   - Customize it to your needs

4. **Connect MCP Servers**
   - Go to "MCP Tools" → "Add MCP Server"
   - Try connecting a GitHub MCP server (requires GitHub token)
   - Use the tools in your agents

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: Changes to `.py` files automatically reload the server
- **Frontend**: Changes to `.tsx`/`.ts` files automatically refresh the browser

### API Documentation

FastAPI provides interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### Database Management

View your data:
```bash
psql agentic_ai

# List tables
\dt

# Query workspaces
SELECT * FROM workspaces;

# Query agents
SELECT id, name, definition_type FROM agents;

# Exit
\q
```

Reset database:
```bash
# Warning: This deletes all data!
dropdb agentic_ai
createdb agentic_ai
cd backend
alembic upgrade head
```

## Common Tasks

### Adding a New Dependency

**Backend:**
```bash
cd backend
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install package-name
# package.json is automatically updated
```

### Running Tests

```bash
# Backend
cd backend
source venv/bin/activate
pytest

# Frontend
cd frontend
npm test
```

### Building for Production

```bash
# Backend
cd backend
source venv/bin/activate
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd frontend
npm run build
# Output will be in dist/
```

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- View API documentation at http://localhost:8000/api/v1/docs
- Check the logs in the terminal where the servers are running

## Success! 🎉

If you can access http://localhost:5173 and see the Agentic AI Platform dashboard, you're all set!

Start by creating your first agent and exploring the features.

