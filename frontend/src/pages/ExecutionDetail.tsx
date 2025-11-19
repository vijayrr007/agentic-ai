import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Clock, CheckCircle, XCircle, Loader, FileText } from 'lucide-react'
import { apiClient } from '@/api/client'

interface Execution {
  id: string
  agent_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  input_data: any
  output_data: any
  started_at: string | null
  completed_at: string | null
  created_at: string
  logs: string | null
  error_message: string | null
}

export default function ExecutionDetail() {
  const { id } = useParams()
  const [execution, setExecution] = useState<Execution | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      fetchExecution()
      // Auto-refresh every 3 seconds if still running
      const interval = setInterval(() => {
        if (execution?.status === 'pending' || execution?.status === 'running') {
          fetchExecution()
        }
      }, 3000)
      return () => clearInterval(interval)
    }
  }, [id, execution?.status])

  const fetchExecution = async () => {
    try {
      const response = await apiClient.get(`/v1/executions/${id}`)
      setExecution(response.data)
      setError(null)
    } catch (err: any) {
      console.error('Error fetching execution:', err)
      setError('Failed to load execution details')
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
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-6 w-6 text-gray-500" />
      case 'running':
        return <Loader className="h-6 w-6 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-500" />
      default:
        return <Clock className="h-6 w-6 text-gray-500" />
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

  const getDuration = () => {
    if (!execution?.started_at) return 'Not started'
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
        <div className="flex items-center gap-4">
          <Link to="/executions" className="p-2 hover:bg-accent rounded-lg">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-3xl font-bold">Loading...</h1>
        </div>
        <div className="rounded-lg border bg-card p-12">
          <div className="text-center">
            <p className="text-muted-foreground">Loading execution details...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !execution) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/executions" className="p-2 hover:bg-accent rounded-lg">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-3xl font-bold">Execution Not Found</h1>
        </div>
        <div className="rounded-lg border border-red-500 bg-red-50 p-6 text-red-800">
          <p className="font-medium">Execution not found</p>
          <p className="text-sm mt-1">{error || 'The requested execution could not be found.'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/executions" className="p-2 hover:bg-accent rounded-lg">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              Execution {execution.id.substring(0, 8)}
              {getStatusIcon(execution.status)}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Created: {formatDate(execution.created_at)}
            </p>
          </div>
        </div>
        <span className={`px-4 py-2 rounded-full text-sm font-medium border ${getStatusColor(execution.status)}`}>
          {execution.status.toUpperCase()}
        </span>
      </div>

      {/* Status Info Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Status</p>
          <p className="text-2xl font-bold capitalize mt-1">{execution.status}</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Duration</p>
          <p className="text-2xl font-bold mt-1">{getDuration()}</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Started</p>
          <p className="text-sm font-medium mt-1">{formatDate(execution.started_at)}</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Completed</p>
          <p className="text-sm font-medium mt-1">{formatDate(execution.completed_at)}</p>
        </div>
      </div>

      {/* Agent Info */}
      <div className="rounded-lg border bg-card p-6">
        <h2 className="text-xl font-semibold mb-4">Agent Information</h2>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Agent ID:</span>
            <Link 
              to={`/agents/${execution.agent_id}`}
              className="text-sm font-mono text-primary hover:underline"
            >
              {execution.agent_id}
            </Link>
          </div>
        </div>
      </div>

      {/* Input Data */}
      {execution.input_data && (
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Input Data
          </h2>
          <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
            {JSON.stringify(execution.input_data, null, 2)}
          </pre>
        </div>
      )}

      {/* Output Data */}
      {execution.output_data && (
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Output Data
          </h2>
          <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
            {JSON.stringify(execution.output_data, null, 2)}
          </pre>
        </div>
      )}

      {/* Error Message */}
      {execution.error_message && (
        <div className="rounded-lg border border-red-500 bg-red-50 p-6">
          <h2 className="text-xl font-semibold text-red-800 mb-4">Error</h2>
          <pre className="text-sm text-red-800 whitespace-pre-wrap">
            {execution.error_message}
          </pre>
        </div>
      )}

      {/* Logs */}
      <div className="rounded-lg border bg-card p-6">
        <h2 className="text-xl font-semibold mb-4">Execution Logs</h2>
        {execution.logs ? (
          <pre className="bg-black text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono">
            {execution.logs}
          </pre>
        ) : (
          <p className="text-muted-foreground text-center py-8">
            {execution.status === 'pending' ? 'Waiting to start...' : 'No logs available'}
          </p>
        )}
      </div>
    </div>
  )
}

