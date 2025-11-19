import { Link } from 'react-router-dom'
import { Plus, Search } from 'lucide-react'

export default function AgentsList() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Agents</h1>
        <Link
          to="/agents/new"
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Create Agent
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search agents..."
            className="w-full rounded-lg border border-input bg-background pl-10 pr-4 py-2"
          />
        </div>
        <select className="rounded-lg border border-input bg-background px-3 py-2">
          <option>All Types</option>
          <option>Visual Builder</option>
          <option>YAML</option>
          <option>Code</option>
        </select>
        <select className="rounded-lg border border-input bg-background px-3 py-2">
          <option>Sort: Recent</option>
          <option>Sort: Name</option>
          <option>Sort: Modified</option>
        </select>
      </div>

      {/* Agents Grid */}
      <div className="rounded-lg border bg-card p-12">
        <div className="text-center">
          <p className="text-muted-foreground">No agents created yet</p>
          <Link
            to="/agents/new"
            className="mt-4 inline-flex items-center gap-2 text-sm text-primary hover:underline"
          >
            <Plus className="h-4 w-4" />
            Create your first agent
          </Link>
        </div>
      </div>
    </div>
  )
}

