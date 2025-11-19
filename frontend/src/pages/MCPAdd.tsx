export default function MCPAdd() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Add MCP Server</h1>
        <div className="flex gap-2">
          <button className="rounded-lg border px-4 py-2 hover:bg-accent">
            Cancel
          </button>
          <button className="rounded-lg bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90">
            Save & Enable
          </button>
        </div>
      </div>

      <div className="rounded-lg border bg-card p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Server Name</label>
          <input
            type="text"
            placeholder="My MCP Server"
            className="w-full rounded-lg border border-input bg-background px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Transport</label>
          <select className="w-full rounded-lg border border-input bg-background px-3 py-2">
            <option>stdio</option>
            <option>SSE</option>
            <option>WebSocket</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Command</label>
          <input
            type="text"
            placeholder="npx"
            className="w-full rounded-lg border border-input bg-background px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Arguments</label>
          <input
            type="text"
            placeholder="-y @modelcontextprotocol/server-*"
            className="w-full rounded-lg border border-input bg-background px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Environment Variables</label>
          <div className="space-y-2">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="KEY"
                className="flex-1 rounded-lg border border-input bg-background px-3 py-2"
              />
              <input
                type="text"
                placeholder="VALUE"
                className="flex-1 rounded-lg border border-input bg-background px-3 py-2"
              />
            </div>
          </div>
        </div>

        <button className="text-sm text-primary hover:underline">
          Test Connection
        </button>
      </div>
    </div>
  )
}

