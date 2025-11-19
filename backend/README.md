# Agentic AI Platform - Backend

FastAPI-based backend for the Agentic AI Platform.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
```bash
brew install postgresql@16
brew services start postgresql@16
createdb agentic_ai
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/api/v1/docs

## Project Structure

- `app/api/` - API endpoints
- `app/core/` - Core configuration and database
- `app/models/` - SQLAlchemy models
- `app/schemas/` - Pydantic schemas
- `app/services/` - Business logic
- `app/utils/` - Utility functions
- `alembic/` - Database migrations

