import { useParams } from 'react-router-dom'

export default function TemplateDetail() {
  const { id } = useParams()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Template: {id}</h1>
      <div className="rounded-lg border bg-card p-6">
        <p className="text-muted-foreground">Template details will be displayed here</p>
      </div>
    </div>
  )
}

