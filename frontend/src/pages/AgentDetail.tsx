import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Save, Play, Trash2 } from 'lucide-react'
import { apiClient } from '@/api/client'

interface Agent {
  id: string
  name: string
  description: string
  definition_type: string
  definition: {
    tools: string[]
    steps: any[]
  }
  workspace_id: string
  version: number
  created_at: string
  updated_at: string
}

export default function AgentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [agent, setAgent] = useState<Agent | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  
  // Editable fields
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [selectedTools, setSelectedTools] = useState<string[]>([])
  
  const availableTools = [
    { id: 'web_search', label: 'Web Search', status: '⚠️ Placeholder' },
    { id: 'file_read', label: 'File Read', status: '✅ Active' },
    { id: 'file_write', label: 'File Write', status: '✅ Active' },
    { id: 'http_request', label: 'HTTP Request', status: '✅ Active' }
  ]

  useEffect(() => {
    if (id) {
      fetchAgent()
    }
  }, [id])

  const fetchAgent = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get(`/v1/agents/${id}`)
      const agentData = response.data
      setAgent(agentData)
      setName(agentData.name)
      setDescription(agentData.description || '')
      setSelectedTools(agentData.definition?.tools || [])
    } catch (err: any) {
      console.error('Error fetching agent:', err)
      setMessage({
        type: 'error',
        text: 'Failed to load agent details'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleToolToggle = (toolId: string) => {
    setSelectedTools(prev =>
      prev.includes(toolId)
        ? prev.filter(t => t !== toolId)
        : [...prev, toolId]
    )
  }

  const handleSave = async () => {
    if (!name.trim()) {
      setMessage({
        type: 'error',
        text: 'Agent name is required'
      })
      return
    }

    setSaving(true)
    setMessage(null)

    try {
      const response = await apiClient.put(`/v1/agents/${id}`, {
        name,
        description,
        definition: {
          ...agent?.definition,
          tools: selectedTools
        }
      })

      setAgent(response.data)
      setMessage({
        type: 'success',
        text: 'Agent updated successfully!'
      })

      // Auto-hide success message after 3 seconds
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      let errorMessage = 'Failed to update agent'
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (Array.isArray(detail)) {
          errorMessage = detail.map((err: any) => `${err.loc?.join('.') || 'Field'}: ${err.msg}`).join(', ')
        } else if (typeof detail === 'string') {
          errorMessage = detail
        }
      }
      
      setMessage({
        type: 'error',
        text: errorMessage
      })
      console.error('Error updating agent:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
      return
    }

    try {
      await apiClient.delete(`/v1/agents/${id}`)
      navigate('/agents')
    } catch (error) {
      console.error('Error deleting agent:', error)
      setMessage({
        type: 'error',
        text: 'Failed to delete agent'
      })
    }
  }

  const handleRun = async () => {
    setMessage(null)
    setSaving(true)

    try {
      // Create an execution
      const response = await apiClient.post('/v1/executions', {
        agent_id: id,
        input_data: {
          message: 'Manual execution triggered from UI',
          timestamp: new Date().toISOString()
        }
      })

      const executionId = response.data.id

      setMessage({
        type: 'success',
        text: `Agent execution started! Execution ID: ${executionId}`
      })

      // Redirect to execution detail page after 2 seconds
      setTimeout(() => {
        navigate(`/executions/${executionId}`)
      }, 2000)
    } catch (error: any) {
      let errorMessage = 'Failed to start agent execution'
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (Array.isArray(detail)) {
          errorMessage = detail.map((err: any) => `${err.loc?.join('.') || 'Field'}: ${err.msg}`).join(', ')
        } else if (typeof detail === 'string') {
          errorMessage = detail
        }
      }
      
      setMessage({
        type: 'error',
        text: errorMessage
      })
      console.error('Error running agent:', error)
    } finally {
      setSaving(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/agents" className="p-2 hover:bg-accent rounded-lg">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-3xl font-bold">Loading...</h1>
        </div>
        <div className="rounded-lg border bg-card p-12">
          <div className="text-center">
            <p className="text-muted-foreground">Loading agent details...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/agents" className="p-2 hover:bg-accent rounded-lg">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-3xl font-bold">Agent Not Found</h1>
        </div>
        <div className="rounded-lg border border-red-500 bg-red-50 p-6 text-red-800">
          <p className="font-medium">Agent not found</p>
          <p className="text-sm mt-1">The requested agent could not be found.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/agents" className="p-2 hover:bg-accent rounded-lg">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold">{agent.name}</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Created: {formatDate(agent.created_at)} • Updated: {formatDate(agent.updated_at)}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleRun}
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-4 w-4" />
            {saving ? 'Starting...' : 'Run Agent'}
          </button>
          <button
            onClick={handleDelete}
            className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        </div>
      </div>

      {/* Success/Error Message */}
      {message && (
        <div
          className={`rounded-lg border p-4 ${
            message.type === 'success'
              ? 'border-green-500 bg-green-50 text-green-800'
              : 'border-red-500 bg-red-50 text-red-800'
          }`}
        >
          <p className="font-medium">
            {message.type === 'success' ? '✓ Success' : '✗ Error'}
          </p>
          <p className="text-sm mt-1">{message.text}</p>
        </div>
      )}

      {/* Edit Form */}
      <div className="rounded-lg border bg-card p-6 space-y-6">
        <h2 className="text-xl font-semibold">Agent Configuration</h2>
        
        {/* Name */}
        <div>
          <label className="block text-sm font-medium mb-2">Agent Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-input bg-background px-3 py-2"
            placeholder="Enter agent name"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium mb-2">Description</label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full rounded-lg border border-input bg-background px-3 py-2"
            placeholder="What does this agent do?"
          />
        </div>

        {/* Tools */}
        <div>
          <label className="block text-sm font-medium mb-2">Available Tools</label>
          <div className="grid grid-cols-2 gap-3">
            {availableTools.map((tool) => (
              <label
                key={tool.id}
                className="flex items-center gap-3 rounded-lg border border-input p-3 hover:bg-accent cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedTools.includes(tool.id)}
                  onChange={() => handleToolToggle(tool.id)}
                  className="h-4 w-4"
                />
                <div className="flex-1">
                  <div className="font-medium">{tool.label}</div>
                  <div className="text-xs text-muted-foreground">{tool.status}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Metadata */}
        <div className="pt-4 border-t">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Type</p>
              <p className="font-medium capitalize">{agent.definition_type}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Version</p>
              <p className="font-medium">v{agent.version}</p>
            </div>
            <div>
              <p className="text-muted-foreground">ID</p>
              <p className="font-mono text-xs">{agent.id}</p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-4 border-t">
          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

