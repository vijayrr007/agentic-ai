# Agentic AI Platform - Frontend

React-based frontend for the Agentic AI Platform.

## Tech Stack

- **React** 18.3+ - UI framework
- **Vite** - Build tool and dev server
- **React Router** v6 - Routing
- **TanStack Query** - Data fetching and caching
- **Zustand** - State management
- **TailwindCSS** - Styling
- **TypeScript** - Type safety
- **Monaco Editor** - Code editing
- **Lucide React** - Icons

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Run development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm test` - Run tests

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── agents/         # Agent-related components
│   ├── workspace/      # Workspace components
│   ├── marketplace/    # Marketplace components
│   ├── execution/      # Execution components
│   ├── mcp/            # MCP tool components
│   └── layout/         # Layout components
├── pages/              # Page components
│   ├── Dashboard.tsx
│   ├── AgentsList.tsx
│   ├── AgentCreate.tsx
│   ├── AgentDetail.tsx
│   ├── ExecutionsList.tsx
│   ├── ExecutionDetail.tsx
│   ├── Marketplace.tsx
│   ├── TemplateDetail.tsx
│   ├── MCPTools.tsx
│   ├── MCPAdd.tsx
│   └── Settings.tsx
├── hooks/              # Custom React hooks
│   ├── useAgents.ts
│   ├── useWorkspace.ts
│   └── useExecutions.ts
├── api/                # API client
│   └── client.ts
├── types/              # TypeScript type definitions
│   └── index.ts
├── App.tsx             # Main app component
├── main.tsx            # App entry point
└── index.css           # Global styles
```

## Key Features

### Agent Creation

Three methods to create agents:
1. **Visual Builder** - Form-based interface
2. **YAML/JSON** - Monaco editor with syntax highlighting
3. **Python Code** - Code editor with validation

### Real-time Updates

Using TanStack Query for automatic data synchronization:
- Automatic cache invalidation
- Optimistic updates
- Background refetching

### Responsive Design

- Desktop: Full sidebar navigation
- Tablet: Collapsible sidebar
- Mobile: Bottom navigation bar

## Styling

Using TailwindCSS with custom color scheme:
- Primary: Blue (`hsl(221.2, 83.2%, 53.3%)`)
- Secondary: Gray (`hsl(210, 40%, 96.1%)`)
- Background: White/Dark mode support

Custom CSS variables defined in `src/index.css`

## API Integration

All API calls go through `src/api/client.ts`:

```typescript
import { apiClient } from '@/api/client'

// Example: Fetch agents
const response = await apiClient.get('/v1/agents')
```

## Adding New Features

1. Create component in appropriate directory
2. Add route in `App.tsx`
3. Create API hook if needed
4. Add TypeScript types in `types/index.ts`
5. Update navigation in `Layout.tsx`

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api)

## Building for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## Code Quality

- **ESLint** - Code linting
- **Prettier** - Code formatting
- **TypeScript** - Type checking

Run checks:
```bash
npm run lint
npm run type-check
```

