import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Bot, Activity, AlertCircle, FileCode, Clock, CheckCircle, XCircle, Loader, Brain } from 'lucide-react'
import { apiClient } from '@/api/client'

interface Agent {
  id: string
  name: string
  description: string
  definition_type: string
  created_at: string
}

interface Execution {
  id: string
  agent_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
  started_at: string | null
  error_message: string | null
}

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalAgents: 0,
    activeRuns: 0,
    recentErrors: 0,
    totalExecutions: 0
  })
  const [recentAgents, setRecentAgents] = useState<Agent[]>([])
  const [recentExecutions, setRecentExecutions] = useState<Execution[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchDashboardData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Fetch agents
      const agentsResponse = await apiClient.get('/v1/agents')
      const agents = agentsResponse.data.agents || []
      
      // Fetch executions
      const executionsResponse = await apiClient.get('/v1/executions')
      const executions = executionsResponse.data.executions || []

      // Calculate stats
      const activeRuns = executions.filter((e: Execution) => 
        e.status === 'running' || e.status === 'pending'
      ).length

      const recentErrors = executions.filter((e: Execution) => 
        e.status === 'failed'
      ).length

      setStats({
        totalAgents: agentsResponse.data.total || agents.length,
        activeRuns,
        recentErrors,
        totalExecutions: executionsResponse.data.total || executions.length
      })

      // Get recent agents (last 5)
      setRecentAgents(agents.slice(0, 5))

      // Get recent executions (last 5)
      setRecentExecutions(executions.slice(0, 5))

      setLoading(false)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-gray-500" />
      case 'running':
        return <Loader className="h-4 w-4 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link
          to="/agents/new"
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          New Agent
        </Link>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Link to="/agents" className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Total Agents</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">{loading ? '...' : stats.totalAgents}</p>
        </Link>
        <Link to="/executions" className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Active Runs</h3>
          </div>
          <p className="mt-2 text-3xl font-bold text-blue-600">{loading ? '...' : stats.activeRuns}</p>
        </Link>
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Failed Runs</h3>
          </div>
          <p className="mt-2 text-3xl font-bold text-red-600">{loading ? '...' : stats.recentErrors}</p>
        </div>
        <Link to="/executions" className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-2">
            <FileCode className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Total Executions</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">{loading ? '...' : stats.totalExecutions}</p>
        </Link>
      </div>

      {/* Recent Executions */}
      <div className="rounded-lg border bg-card">
        <div className="border-b p-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Recent Executions</h2>
          <Link to="/executions" className="text-sm text-primary hover:underline">
            View All
          </Link>
        </div>
        <div className="p-6">
          {loading ? (
            <p className="text-center text-muted-foreground">Loading...</p>
          ) : recentExecutions.length === 0 ? (
            <p className="text-center text-muted-foreground">No executions yet</p>
          ) : (
            <div className="space-y-3">
              {recentExecutions.map((execution) => (
                <Link
                  key={execution.id}
                  to={`/executions/${execution.id}`}
                  className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent transition-colors"
                >
                  <div className="flex items-center gap-3">
                    {getStatusIcon(execution.status)}
                    <div>
                      <p className="text-sm font-medium">Execution {execution.id.substring(0, 8)}</p>
                      <p className="text-xs text-muted-foreground">
                        Agent: {execution.agent_id.substring(0, 8)}... • {formatDate(execution.created_at)}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(execution.status)}`}>
                    {execution.status.toUpperCase()}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Access */}
      <div className="rounded-lg border bg-card">
        <div className="border-b p-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Recent Agents</h2>
          <Link to="/agents" className="text-sm text-primary hover:underline">
            View All
          </Link>
        </div>
        <div className="p-6">
          {loading ? (
            <p className="text-center text-muted-foreground">Loading...</p>
          ) : recentAgents.length === 0 ? (
            <div className="text-center">
              <p className="text-muted-foreground">No agents created yet</p>
              <div className="mt-4">
                <Link
                  to="/agents/new"
                  className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
                >
                  <Plus className="h-4 w-4" />
                  Create your first agent
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {recentAgents.map((agent) => (
                <Link
                  key={agent.id}
                  to={`/agents/${agent.id}`}
                  className="flex items-start gap-3 p-3 rounded-lg border hover:bg-accent transition-colors"
                >
                  <Brain className="h-5 w-5 text-primary mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{agent.name}</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {agent.description || 'No description'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDate(agent.created_at)}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

