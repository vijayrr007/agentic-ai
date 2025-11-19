import { useState } from 'react'
import { apiClient } from '@/api/client'

export default function Settings() {
  const [name, setName] = useState('Default Workspace')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const handleSave = async () => {
    setLoading(true)
    setMessage(null)

    try {
      // For now, create a new workspace (later we'll add update logic)
      const response = await apiClient.post('/v1/workspaces', {
        name,
        description
      })

      setMessage({
        type: 'success',
        text: `Workspace "${name}" saved successfully!`
      })

      console.log('Workspace created:', response.data)
    } catch (error: any) {
      let errorMessage = 'Failed to save workspace. Please try again.'
      
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
      console.error('Error saving workspace:', error)
      console.error('Error details:', error.response?.data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Workspace Settings</h1>

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

      <div className="rounded-lg border bg-card">
        <div className="border-b p-6">
          <h2 className="text-xl font-semibold">General</h2>
        </div>
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Workspace Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-input bg-background px-3 py-2"
              placeholder="Enter workspace name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-lg border border-input bg-background px-3 py-2"
              placeholder="Optional description"
            />
          </div>
          <button
            onClick={handleSave}
            disabled={loading || !name.trim()}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

