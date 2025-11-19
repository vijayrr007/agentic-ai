import { useParams } from 'react-router-dom'

export default function ExecutionDetail() {
  const { id } = useParams()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Execution: {id}</h1>
      <div className="rounded-lg border bg-card p-6">
        <p className="text-muted-foreground">Execution details and logs will be displayed here</p>
      </div>
    </div>
  )
}

