# Agentic AI Platform

A full-featured platform for developers and platform engineers to create, manage, and execute AI agents with MCP (Model Context Protocol) tool integration.

## Features

- **Multi-Format Agent Creation**: Build agents using Visual Builder, YAML/JSON, or Python code
- **MCP Integration**: Connect to MCP servers and use both built-in and custom tools
- **Agent Marketplace**: Share and discover agent templates
- **Workspace Collaboration**: Organize agents in workspaces with team collaboration
- **Execution Monitoring**: Real-time execution logs and status tracking
- **Template System**: Clone and customize pre-built agent templates

## Architecture

- **Frontend**: React + Vite + TailwindCSS + TypeScript
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **Agent Execution**: Isolated subprocess execution
- **Protocol Support**: MCP (stdio, SSE, WebSocket)

## Prerequisites

- Python 3.14+ (you have 3.14.0 ✓)
- Node.js 24+ (you have v24.5.0 ✓)
- PostgreSQL 16+ (needs installation)
- Homebrew (you have 4.6.16 ✓)

## Quick Start

### 1. Install PostgreSQL

```bash
brew install postgresql@16
brew services start postgresql@16
createdb agentic_ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/api/v1/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Project Structure

```
agentic-ai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration & database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   └── requirements.txt
│
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── pages/          # Page components
    │   ├── hooks/          # Custom hooks
    │   ├── api/            # API client
    │   └── types/          # TypeScript types
    ├── package.json
    └── vite.config.ts
```

## API Endpoints

### Workspaces
- `GET /api/v1/workspaces` - List workspaces
- `POST /api/v1/workspaces` - Create workspace
- `GET /api/v1/workspaces/{id}` - Get workspace
- `PUT /api/v1/workspaces/{id}` - Update workspace
- `DELETE /api/v1/workspaces/{id}` - Delete workspace

### Agents
- `GET /api/v1/agents` - List agents
- `POST /api/v1/agents` - Create agent
- `GET /api/v1/agents/{id}` - Get agent
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent
- `POST /api/v1/agents/{id}/duplicate` - Duplicate agent

### Executions
- `GET /api/v1/executions` - List executions
- `POST /api/v1/executions` - Start execution
- `GET /api/v1/executions/{id}` - Get execution
- `GET /api/v1/executions/{id}/logs` - Get logs
- `DELETE /api/v1/executions/{id}` - Cancel execution
- `POST /api/v1/executions/{id}/retry` - Retry execution

### Templates
- `GET /api/v1/templates` - Browse templates
- `POST /api/v1/templates` - Create template
- `GET /api/v1/templates/{id}` - Get template
- `POST /api/v1/templates/{id}/clone` - Clone template

### MCP Tools
- `GET /api/v1/mcp/servers` - List MCP servers
- `POST /api/v1/mcp/servers` - Add MCP server
- `GET /api/v1/mcp/servers/{id}` - Get server
- `GET /api/v1/mcp/builtin` - List built-in tools
- `POST /api/v1/mcp/tools/call` - Execute tool

## Creating Your First Agent

### Option 1: Visual Builder

1. Navigate to "Agents" → "Create Agent"
2. Select "Visual Builder" tab
3. Fill in agent name and description
4. Select tools (web_search, file operations, etc.)
5. Define workflow steps
6. Save and run

### Option 2: YAML Definition

```yaml
agent:
  name: "Web Scraper"
  description: "Scrapes websites and extracts content"
  tools:
    - web_search
    - http_request
    - file_write
  steps:
    - action: "search"
      tool: "web_search"
      params:
        query: "{input.query}"
    - action: "fetch"
      tool: "http_request"
      params:
        url: "{step1.url}"
    - action: "save"
      tool: "file_write"
      params:
        path: "output.txt"
        content: "{step2.body}"
```

### Option 3: Python Code

```python
from agentic import Agent, tool

class WebScraperAgent(Agent):
    """Agent for scraping web content."""
    
    @tool(web_search, http_request, file_write)
    def run(self, query: str):
        # Search for URLs
        results = self.tools.web_search(query)
        
        # Fetch content
        for result in results:
            content = self.tools.http_request(result['url'])
            
            # Save to file
            self.tools.file_write(f"output.txt", content['body'])
        
        return {"status": "completed", "files_created": len(results)}
```

## Configuring MCP Servers

### Example: GitHub MCP Server

1. Navigate to "MCP Tools" → "Add MCP Server"
2. Configure:
   - Name: "GitHub MCP"
   - Transport: stdio
   - Command: `npx`
   - Arguments: `-y @modelcontextprotocol/server-github`
   - Environment Variables:
     - `GITHUB_TOKEN`: `your_github_token`
3. Test connection
4. Use tools in your agents

## Built-in Tools

- **web_search**: Search the web for information
- **file_read**: Read files from disk
- **file_write**: Write content to files
- **file_list**: List directory contents
- **http_request**: Make HTTP requests

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Backend
cd backend
black app/
flake8 app/

# Frontend
cd frontend
npm run lint
npm run format
```

## Environment Variables

### Backend (.env)

```
DATABASE_URL=postgresql://localhost/agentic_ai
API_V1_PREFIX=/api/v1
PROJECT_NAME=Agentic AI Platform
DEBUG=True
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000/api
```

## Deployment

### Backend (FastAPI)

```bash
# Build
cd backend
pip install -r requirements.txt

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (React)

```bash
# Build
cd frontend
npm run build

# Serve with nginx or similar
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/agentic-ai/issues)
- Documentation: See `/docs` directory

## Roadmap

- [x] Multi-format agent creation
- [x] MCP protocol integration
- [x] Agent marketplace
- [x] Workspace management
- [ ] Authentication & authorization
- [ ] Scheduled agent execution
- [ ] Advanced monitoring & alerting
- [ ] Agent versioning & rollback
- [ ] Collaborative editing
- [ ] Docker containerization support
