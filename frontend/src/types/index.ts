export interface Workspace {
  id: string
  name: string
  description?: string
  created_at: string
}

export interface Agent {
  id: string
  workspace_id: string
  name: string
  description?: string
  definition_type: 'ui' | 'yaml' | 'code'
  definition: any
  created_at: string
  updated_at: string
  version: number
}

export interface Execution {
  id: string
  agent_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  started_at?: string
  completed_at?: string
  logs?: string
  error_message?: string
}

export interface Template {
  id: string
  name: string
  description?: string
  definition: any
  category: string
  is_public: boolean
  author_workspace_id: string
  usage_count?: number
}

export interface MCPServer {
  id: string
  workspace_id: string
  name: string
  server_type: 'builtin' | 'custom'
  transport: 'stdio' | 'sse' | 'websocket'
  config: any
  enabled: boolean
  status?: 'connected' | 'disconnected' | 'error'
}

