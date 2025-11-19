import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Clock, CheckCircle, XCircle, PlayCircle, Loader } from 'lucide-react'
import { apiClient } from '@/api/client'

interface Execution {
  id: string
  agent_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at: string | null
  completed_at: string | null
  created_at: string
  error_message: string | null
}

export default function ExecutionsList() {
  const [executions, setExecutions] = useState<Execution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchExecutions()
    // Auto-refresh every 5 seconds to show status updates
    const interval = setInterval(fetchExecutions, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchExecutions = async () => {
    try {
      const response = await apiClient.get('/v1/executions')
      setExecutions(response.data.executions || [])
      setError(null)
    } catch (err: any) {
      console.error('Error fetching executions:', err)
      setError('Failed to load executions')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-gray-500" />
      case 'running':
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <PlayCircle className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800 border-gray-300'
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getDuration = (execution: Execution) => {
    if (!execution.started_at) return 'Not started'
    const start = new Date(execution.started_at).getTime()
    const end = execution.completed_at 
      ? new Date(execution.completed_at).getTime() 
      : Date.now()
    const duration = Math.floor((end - start) / 1000)
    return `${duration}s`
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Execution History</h1>
        <div className="rounded-lg border bg-card p-12">
          <div className="text-center">
            <p className="text-muted-foreground">Loading executions...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Execution History</h1>
        <p className="text-sm text-muted-foreground">Auto-refreshes every 5 seconds</p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500 bg-red-50 p-4 text-red-800">
          <p className="font-medium">✗ Error</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {executions.length === 0 && !error && (
        <div className="rounded-lg border bg-card p-12">
          <div className="text-center">
            <p className="text-muted-foreground">No executions yet</p>
            <p className="text-sm text-muted-foreground mt-2">
              Run an agent to see executions here
            </p>
          </div>
        </div>
      )}

      {executions.length > 0 && (
        <div className="space-y-3">
          {executions.map((execution) => (
            <Link
              key={execution.id}
              to={`/executions/${execution.id}`}
              className="block rounded-lg border bg-card p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  {getStatusIcon(execution.status)}
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold">Execution {execution.id.substring(0, 8)}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(execution.status)}`}>
                        {execution.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Agent ID: {execution.agent_id.substring(0, 8)}...
                    </p>
                  </div>
                </div>

                <div className="text-right text-sm text-muted-foreground">
                  <p>Started: {formatDate(execution.started_at)}</p>
                  <p>Duration: {getDuration(execution)}</p>
                </div>
              </div>

              {execution.error_message && (
                <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                  Error: {execution.error_message}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

