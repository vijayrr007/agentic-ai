import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Brain, Calendar, Edit, Trash2 } from 'lucide-react'
import { apiClient } from '@/api/client'

interface Agent {
  id: string
  name: string
  description: string
  definition_type: string
  created_at: string
  updated_at: string
}

export default function AgentsList() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/v1/agents')
      setAgents(response.data.agents || [])
      setError(null)
    } catch (err: any) {
      console.error('Error fetching agents:', err)
      setError('Failed to load agents')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
      return
    }

    try {
      await apiClient.delete(`/v1/agents/${id}`)
      setAgents(agents.filter(a => a.id !== id))
    } catch (err) {
      console.error('Error deleting agent:', err)
      alert('Failed to delete agent')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      ui: 'Visual Builder',
      yaml: 'YAML/JSON',
      code: 'Python Code'
    }
    return labels[type] || type
  }

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

      {/* Loading State */}
      {loading && (
        <div className="rounded-lg border bg-card p-12">
          <div className="text-center">
            <p className="text-muted-foreground">Loading agents...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="rounded-lg border border-red-500 bg-red-50 p-4 text-red-800">
          <p className="font-medium">✗ Error</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Agents Grid */}
      {!loading && !error && agents.length === 0 && (
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
      )}

      {!loading && !error && agents.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold text-lg">{agent.name}</h3>
                </div>
                <div className="flex gap-1">
                  <Link
                    to={`/agents/${agent.id}`}
                    className="p-1 hover:bg-accent rounded"
                    title="View details"
                  >
                    <Edit className="h-4 w-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(agent.id, agent.name)}
                    className="p-1 hover:bg-accent rounded text-red-600"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                {agent.description || 'No description'}
              </p>

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-accent">
                  {getTypeLabel(agent.definition_type)}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {formatDate(agent.created_at)}
                </span>
              </div>

              <Link
                to={`/agents/${agent.id}`}
                className="mt-4 block w-full text-center rounded-lg border border-primary px-4 py-2 text-sm font-medium text-primary hover:bg-primary hover:text-primary-foreground transition-colors"
              >
                View Details
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

