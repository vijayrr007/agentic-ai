import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import AgentsList from './pages/AgentsList'
import AgentCreate from './pages/AgentCreate'
import AgentDetail from './pages/AgentDetail'
import ExecutionsList from './pages/ExecutionsList'
import ExecutionDetail from './pages/ExecutionDetail'
import Marketplace from './pages/Marketplace'
import TemplateDetail from './pages/TemplateDetail'
import MCPTools from './pages/MCPTools'
import MCPAdd from './pages/MCPAdd'
import Settings from './pages/Settings'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<AgentsList />} />
        <Route path="/agents/new" element={<AgentCreate />} />
        <Route path="/agents/:id" element={<AgentDetail />} />
        <Route path="/agents/:id/edit" element={<AgentCreate />} />
        <Route path="/executions" element={<ExecutionsList />} />
        <Route path="/executions/:id" element={<ExecutionDetail />} />
        <Route path="/marketplace" element={<Marketplace />} />
        <Route path="/marketplace/:id" element={<TemplateDetail />} />
        <Route path="/mcp" element={<MCPTools />} />
        <Route path="/mcp/add" element={<MCPAdd />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App

