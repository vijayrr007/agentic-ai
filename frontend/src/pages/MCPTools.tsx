import { Link } from 'react-router-dom'
import { Plus } from 'lucide-react'

export default function MCPTools() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">MCP Tools & Servers</h1>
        <Link
          to="/mcp/add"
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Add MCP Server
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button className="px-4 py-2 border-b-2 border-primary text-primary">
          Configured Servers
        </button>
        <button className="px-4 py-2 border-b-2 border-transparent text-muted-foreground hover:text-foreground">
          Built-in Tools
        </button>
      </div>

      {/* Content */}
      <div className="rounded-lg border bg-card p-12">
        <div className="text-center">
          <p className="text-muted-foreground">No MCP servers configured yet</p>
          <Link
            to="/mcp/add"
            className="mt-4 inline-flex items-center gap-2 text-sm text-primary hover:underline"
          >
            <Plus className="h-4 w-4" />
            Add your first MCP server
          </Link>
        </div>
      </div>
    </div>
  )
}

