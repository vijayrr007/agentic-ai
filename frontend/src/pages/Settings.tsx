export default function Settings() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Workspace Settings</h1>

      <div className="rounded-lg border bg-card">
        <div className="border-b p-6">
          <h2 className="text-xl font-semibold">General</h2>
        </div>
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Workspace Name</label>
            <input
              type="text"
              defaultValue="Default Workspace"
              className="w-full rounded-lg border border-input bg-background px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              rows={3}
              className="w-full rounded-lg border border-input bg-background px-3 py-2"
            />
          </div>
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  )
}

