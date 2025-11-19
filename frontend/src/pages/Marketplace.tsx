import { Search } from 'lucide-react'

export default function Marketplace() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Agent Marketplace</h1>
        <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          Publish Agent
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search templates..."
          className="w-full rounded-lg border border-input bg-background pl-10 pr-4 py-2"
        />
      </div>

      {/* Categories */}
      <div className="flex gap-2">
        <button className="rounded-lg border px-4 py-2 text-sm hover:bg-accent">All</button>
        <button className="rounded-lg border px-4 py-2 text-sm hover:bg-accent">Web Scraping</button>
        <button className="rounded-lg border px-4 py-2 text-sm hover:bg-accent">Data</button>
        <button className="rounded-lg border px-4 py-2 text-sm hover:bg-accent">Automation</button>
      </div>

      {/* Templates Grid */}
      <div className="rounded-lg border bg-card p-12">
        <div className="text-center">
          <p className="text-muted-foreground">No templates available yet</p>
        </div>
      </div>
    </div>
  )
}

