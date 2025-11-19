import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileCode, Code, FileJson } from 'lucide-react'
import { apiClient } from '@/api/client'

type CreationMode = 'visual' | 'yaml' | 'code'

export default function AgentCreate() {
  const [mode, setMode] = useState<CreationMode>('visual')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const navigate = useNavigate()

  // Form state
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [selectedTools, setSelectedTools] = useState<string[]>([])

  const handleToolToggle = (tool: string) => {
    setSelectedTools(prev =>
      prev.includes(tool)
        ? prev.filter(t => t !== tool)
        : [...prev, tool]
    )
  }

  const handleSave = async () => {
    if (!name.trim()) {
      setMessage({
        type: 'error',
        text: 'Please enter an agent name'
      })
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      // Get workspaces first to use the first one
      const workspacesResponse = await apiClient.get('/v1/workspaces')
      const workspaces = workspacesResponse.data
      
      if (!workspaces || workspaces.length === 0) {
        setMessage({
          type: 'error',
          text: 'Please create a workspace first in Settings'
        })
        setLoading(false)
        return
      }

      const workspaceId = workspaces[0].id

      // Create agent
      // Map frontend mode to backend definition_type
      const definitionType = mode === 'visual' ? 'ui' : mode
      
      const response = await apiClient.post('/v1/agents', {
        workspace_id: workspaceId,
        name,
        description,
        definition_type: definitionType,
        definition: {
          tools: selectedTools,
          steps: []
        }
      })

      setMessage({
        type: 'success',
        text: `Agent "${name}" created successfully!`
      })

      // Redirect to agent detail after 1.5 seconds
      setTimeout(() => {
        navigate(`/agents/${response.data.id}`)
      }, 1500)

    } catch (error: any) {
      let errorMessage = 'Failed to create agent. Please try again.'
      
      // Handle FastAPI validation errors (422)
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (Array.isArray(detail)) {
          // Validation error array from FastAPI
          errorMessage = detail.map((err: any) => `${err.loc?.join('.') || 'Field'}: ${err.msg}`).join(', ')
        } else if (typeof detail === 'string') {
          errorMessage = detail
        } else if (typeof detail === 'object') {
          errorMessage = JSON.stringify(detail)
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setMessage({
        type: 'error',
        text: errorMessage
      })
      console.error('Error creating agent:', error)
      console.error('Error details:', error.response?.data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
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

      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Create New Agent</h1>
        <div className="flex gap-2">
          <button 
            onClick={() => navigate('/agents')}
            className="rounded-lg border px-4 py-2 hover:bg-accent"
          >
            Cancel
          </button>
          <button 
            onClick={handleSave}
            disabled={loading}
            className="rounded-lg bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* Creation Mode Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setMode('visual')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
            mode === 'visual'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <FileCode className="h-4 w-4" />
          Visual Builder
        </button>
        <button
          onClick={() => setMode('yaml')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
            mode === 'yaml'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <FileJson className="h-4 w-4" />
          YAML/JSON
        </button>
        <button
          onClick={() => setMode('code')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
            mode === 'code'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Code className="h-4 w-4" />
          Python Code
        </button>
      </div>

      {/* Content based on mode */}
      <div className="rounded-lg border bg-card p-6">
        {mode === 'visual' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Agent Name</label>
              <input
                type="text"
                placeholder="My Agent"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                placeholder="What does this agent do?"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Available Tools</label>
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center gap-2">
                  <input 
                    type="checkbox" 
                    checked={selectedTools.includes('web_search')}
                    onChange={() => handleToolToggle('web_search')}
                  />
                  <span>Web Search</span>
                </label>
                <label className="flex items-center gap-2">
                  <input 
                    type="checkbox"
                    checked={selectedTools.includes('file_write')}
                    onChange={() => handleToolToggle('file_write')}
                  />
                  <span>File Write</span>
                </label>
                <label className="flex items-center gap-2">
                  <input 
                    type="checkbox"
                    checked={selectedTools.includes('file_read')}
                    onChange={() => handleToolToggle('file_read')}
                  />
                  <span>File Read</span>
                </label>
                <label className="flex items-center gap-2">
                  <input 
                    type="checkbox"
                    checked={selectedTools.includes('http_request')}
                    onChange={() => handleToolToggle('http_request')}
                  />
                  <span>HTTP Request</span>
                </label>
              </div>
            </div>
          </div>
        )}
        {mode === 'yaml' && (
          <div>
            <p className="text-sm text-muted-foreground mb-4">
              Upload or paste your YAML/JSON agent definition
            </p>
            <textarea
              placeholder="agent:&#10;  name: My Agent&#10;  description: What it does&#10;  tools:&#10;    - web_search&#10;  steps:&#10;    - ..."
              rows={15}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 font-mono text-sm"
            />
          </div>
        )}
        {mode === 'code' && (
          <div>
            <p className="text-sm text-muted-foreground mb-4">
              Write your agent in Python
            </p>
            <textarea
              placeholder="from agentic import Agent&#10;&#10;class MyAgent(Agent):&#10;    def run(self, input):&#10;        # Your code here&#10;        pass"
              rows={15}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 font-mono text-sm"
            />
          </div>
        )}
      </div>
    </div>
  )
}

