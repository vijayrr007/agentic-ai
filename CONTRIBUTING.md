# Contributing to Agentic AI Platform

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/agentic-ai.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request

## Development Setup

Follow the [SETUP.md](SETUP.md) guide to set up your development environment.

## Code Style

### Backend (Python)

We use:
- **Black** for code formatting
- **Flake8** for linting
- **Type hints** for all functions

Format your code before committing:
```bash
cd backend
black app/
flake8 app/
```

Example:
```python
from typing import Optional

def create_agent(name: str, description: Optional[str] = None) -> Agent:
    """
    Create a new agent.
    
    Args:
        name: Agent name
        description: Optional description
        
    Returns:
        Created agent instance
    """
    pass
```

### Frontend (TypeScript/React)

We use:
- **ESLint** for linting
- **Prettier** for formatting
- **TypeScript** strict mode

Format your code before committing:
```bash
cd frontend
npm run lint
npm run format  # If available
```

Example:
```typescript
interface AgentProps {
  name: string
  description?: string
}

export function AgentCard({ name, description }: AgentProps) {
  return (
    <div className="rounded-lg border p-4">
      <h3>{name}</h3>
      {description && <p>{description}</p>}
    </div>
  )
}
```

## Commit Messages

Use clear, descriptive commit messages:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(agents): add agent duplication feature

Add endpoint and UI for duplicating existing agents
with all their configuration and tools.

Closes #123
```

```
fix(execution): handle timeout errors gracefully

Previously, timeout errors would crash the execution engine.
Now they are caught and logged properly.
```

## Pull Request Process

1. **Update documentation** if you've changed APIs or added features
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** (if applicable)
5. **Request review** from maintainers

### PR Title Format

Use the same format as commit messages:
```
feat(scope): description
fix(scope): description
docs: description
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest

# Run specific test
pytest tests/test_agents.py

# With coverage
pytest --cov=app tests/
```

### Frontend Tests

```bash
cd frontend
npm test

# Watch mode
npm test -- --watch

# With coverage
npm test -- --coverage
```

## Adding Features

### Backend API Endpoint

1. **Add route** in `backend/app/api/`
2. **Add schema** in `backend/app/schemas/`
3. **Add model** if needed in `backend/app/models/`
4. **Add tests** in `backend/tests/`

Example:
```python
# app/api/agents.py
@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """Create a new agent."""
    agent = Agent(**agent_data.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent
```

### Frontend Component

1. **Create component** in `frontend/src/components/`
2. **Add types** in `frontend/src/types/`
3. **Add to router** if it's a page
4. **Add tests**

Example:
```typescript
// src/components/agents/AgentCard.tsx
import { Agent } from '@/types'

interface AgentCardProps {
  agent: Agent
  onRun: (id: string) => void
}

export function AgentCard({ agent, onRun }: AgentCardProps) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="font-semibold">{agent.name}</h3>
      <p className="text-sm text-muted-foreground">{agent.description}</p>
      <button onClick={() => onRun(agent.id)}>Run</button>
    </div>
  )
}
```

## Database Migrations

When changing database models:

```bash
cd backend
source venv/bin/activate

# Create migration
alembic revision --autogenerate -m "description"

# Review the migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Documentation

- Update README.md for new features
- Add docstrings to all functions
- Update API documentation if endpoints change
- Add inline comments for complex logic

## Code Review Guidelines

When reviewing PRs:

- ✅ **Do:**
  - Be constructive and respectful
  - Explain why changes are needed
  - Suggest specific improvements
  - Approve when ready

- ❌ **Don't:**
  - Make personal comments
  - Nitpick minor style issues (use linters)
  - Block PRs without explanation

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues/discussions first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You! 🎉

Your contributions help make this project better for everyone!

