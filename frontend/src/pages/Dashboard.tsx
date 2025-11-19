import { Link } from 'react-router-dom'
import { Plus, Bot, Activity, AlertCircle, FileCode } from 'lucide-react'

export default function Dashboard() {
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
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Total Agents</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Active Runs</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Recent Errors</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-2">
            <FileCode className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Templates Used</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>
      </div>

      {/* Recent Executions */}
      <div className="rounded-lg border bg-card">
        <div className="border-b p-6">
          <h2 className="text-xl font-semibold">Recent Executions</h2>
        </div>
        <div className="p-6">
          <p className="text-center text-muted-foreground">No recent executions</p>
        </div>
      </div>

      {/* Quick Access */}
      <div className="rounded-lg border bg-card">
        <div className="border-b p-6">
          <h2 className="text-xl font-semibold">Quick Access</h2>
        </div>
        <div className="p-6">
          <p className="text-center text-muted-foreground">No agents created yet</p>
          <div className="mt-4 text-center">
            <Link
              to="/agents/new"
              className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
            >
              <Plus className="h-4 w-4" />
              Create your first agent
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

