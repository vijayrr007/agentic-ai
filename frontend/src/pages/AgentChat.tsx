import { useState, useEffect, useRef } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Send, Loader, User, Bot, Plus } from 'lucide-react'
import { apiClient } from '@/api/client'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

interface Conversation {
  id: string
  agent_id: string
  title: string
  created_at: string
  messages: Message[]
}

interface Agent {
  id: string
  name: string
  description: string
}

export default function AgentChat() {
  const { agentId, conversationId } = useParams()
  const navigate = useNavigate()
  const [agent, setAgent] = useState<Agent | null>(null)
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [loading, setLoading] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (agentId) {
      fetchAgent()
      if (conversationId) {
        fetchConversation()
      } else {
        createNewConversation()
      }
    }
  }, [agentId, conversationId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchAgent = async () => {
    try {
      const response = await apiClient.get(`/v1/agents/${agentId}`)
      setAgent(response.data)
    } catch (error) {
      console.error('Error fetching agent:', error)
    }
  }

  const createNewConversation = async () => {
    try {
      const response = await apiClient.post('/v1/conversations', {
        agent_id: agentId
      })
      const newConversation = response.data
      setConversation(newConversation)
      setMessages(newConversation.messages || [])
      // Update URL to include conversation ID
      navigate(`/agents/${agentId}/chat/${newConversation.id}`, { replace: true })
    } catch (error) {
      console.error('Error creating conversation:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchConversation = async () => {
    try {
      const response = await apiClient.get(`/v1/conversations/${conversationId}`)
      setConversation(response.data)
      setMessages(response.data.messages || [])
    } catch (error) {
      console.error('Error fetching conversation:', error)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !conversationId || sending) return

    const userMessage = input.trim()
    setInput('')
    setSending(true)

    // Optimistically add user message to UI
    const tempUserMessage: Message = {
      id: 'temp-user',
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMessage])

    try {
      const response = await apiClient.post(`/v1/conversations/${conversationId}/messages`, {
        content: userMessage
      })

      // Replace temp message with real messages
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== 'temp-user')
        return [
          ...filtered,
          response.data.message,
          ...(response.data.assistant_message ? [response.data.assistant_message] : [])
        ]
      })
    } catch (error) {
      console.error('Error sending message:', error)
      // Remove temp message on error
      setMessages(prev => prev.filter(m => m.id !== 'temp-user'))
      alert('Failed to send message. Please try again.')
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatMessageContent = (content: string) => {
    // Simple formatting for markdown-like content
    return content.split('\n').map((line, i) => (
      <span key={i}>
        {line}
        {i < content.split('\n').length - 1 && <br />}
      </span>
    ))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <Loader className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4 bg-card">
        <div className="flex items-center gap-4">
          <Link to={`/agents/${agentId}`} className="p-2 hover:bg-accent rounded-lg">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-xl font-bold">Chat with {agent?.name}</h1>
            <p className="text-sm text-muted-foreground">{agent?.description}</p>
          </div>
        </div>
        <button
          onClick={createNewConversation}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          New Chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.filter(m => m.role !== 'system').map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <Bot className="h-5 w-5 text-primary-foreground" />
              </div>
            )}
            
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted'
              }`}
            >
              <div className="text-sm whitespace-pre-wrap">
                {formatMessageContent(message.content)}
              </div>
              <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                {new Date(message.created_at).toLocaleTimeString()}
              </div>
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent flex items-center justify-center">
                <User className="h-5 w-5" />
              </div>
            )}
          </div>
        ))}

        {sending && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Bot className="h-5 w-5 text-primary-foreground" />
            </div>
            <div className="bg-muted rounded-lg p-3">
              <Loader className="h-4 w-4 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4 bg-card">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 rounded-lg border border-input bg-background px-4 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-primary"
            rows={1}
            disabled={sending}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || sending}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}


