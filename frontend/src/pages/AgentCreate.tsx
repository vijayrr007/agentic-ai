import { useState } from 'react'
import { FileCode, Code, FileJson } from 'lucide-react'

type CreationMode = 'visual' | 'yaml' | 'code'

export default function AgentCreate() {
  const [mode, setMode] = useState<CreationMode>('visual')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Create New Agent</h1>
        <div className="flex gap-2">
          <button className="rounded-lg border px-4 py-2 hover:bg-accent">
            Cancel
          </button>
          <button className="rounded-lg bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90">
            Save
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
                className="w-full rounded-lg border border-input bg-background px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                placeholder="What does this agent do?"
                rows={3}
                className="w-full rounded-lg border border-input bg-background px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Available Tools</label>
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center gap-2">
                  <input type="checkbox" />
                  <span>Web Search</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" />
                  <span>File Operations</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" />
                  <span>HTTP Request</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" />
                  <span>Code Execution</span>
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

