# Agent Chat Feature

## Overview
The chat feature allows users to have conversational interactions with agents. Each conversation maintains history, and agents can use their configured tools (web search, file operations, HTTP requests) to respond to user messages.

## Components

### Backend

#### Models
- **Conversation** (`backend/app/models/conversation.py`)
  - Stores chat sessions with agents
  - Fields: id, agent_id, title, created_at, updated_at
  - Relationships: agent, messages

- **Message** (`backend/app/models/message.py`)
  - Stores individual messages in conversations
  - Fields: id, conversation_id, role (user/assistant/system), content, created_at
  - Relationships: conversation

#### API Endpoints (`backend/app/api/conversations.py`)
- `GET /v1/conversations/` - List all conversations (with optional agent_id filter)
- `POST /v1/conversations/` - Create new conversation
- `GET /v1/conversations/{id}` - Get conversation with all messages
- `POST /v1/conversations/{id}/messages` - Send message and get agent response
- `DELETE /v1/conversations/{id}` - Delete conversation

#### Database
- Migration: `e4b25f86b33d_add_conversations_and_messages_tables.py`
- Tables: `conversations`, `messages`

### Frontend

#### Pages
- **AgentChat** (`frontend/src/pages/AgentChat.tsx`)
  - Full-featured chat interface
  - Real-time message display
  - User input with keyboard shortcuts (Enter to send, Shift+Enter for newline)
  - New chat button
  - Message history with timestamps
  - Responsive design

#### Routes
- `/agents/:agentId/chat` - Start new chat
- `/agents/:agentId/chat/:conversationId` - View existing conversation

#### Integration
- "Chat" button added to agent detail page header
- Blue-colored button next to "Run Agent" button

## Features

### Chat Flow
1. User navigates to agent detail page
2. Clicks "Chat" button
3. New conversation is automatically created
4. User can type messages and send them
5. Agent processes the message using its configured tools
6. Assistant response is displayed in real-time
7. Conversation history is maintained

### Agent Capabilities in Chat
- **Web Search**: If agent has `web_search` tool, it can search the web based on user queries
- **File Operations**: Can read/write files if configured
- **HTTP Requests**: Can make HTTP calls if configured
- **Context Awareness**: Agent receives full conversation history with each message

### Message Formatting
- User messages: Right-aligned, blue background
- Assistant messages: Left-aligned, gray background
- System messages: Hidden from UI (used for agent prompts)
- Timestamps displayed for all messages
- Multi-line support with preserved formatting

## Usage

### Start a Chat
```
1. Go to Agents page
2. Click on an agent to view details
3. Click the "Chat" button (blue button in header)
4. Start typing and sending messages
```

### API Usage

#### Create Conversation
```bash
curl -X POST http://localhost:8000/api/v1/conversations/ \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id", "title": "Optional title"}'
```

#### Send Message
```bash
curl -X POST http://localhost:8000/api/v1/conversations/{conversation_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Your message here"}'
```

#### List Conversations
```bash
# All conversations
curl http://localhost:8000/api/v1/conversations/

# Filter by agent
curl http://localhost:8000/api/v1/conversations/?agent_id={agent_id}
```

## Technical Details

### Agent Execution in Chat Mode
- Each message triggers an agent execution
- Agent receives: user message + conversation history
- For web_search agents: message content is used as search query
- Results are formatted into natural language responses
- Execution runs in thread pool to avoid blocking

### Response Formatting
- Web search results: Formatted with titles, snippets, and links
- File operations: Show file path and content preview
- HTTP requests: Display URL and status code
- Errors: Gracefully handled and displayed to user

### Database Schema
```sql
-- conversations table
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    agent_id VARCHAR REFERENCES agents(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- messages table
CREATE TABLE messages (
    id VARCHAR PRIMARY KEY,
    conversation_id VARCHAR REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR (user/assistant/system),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Future Enhancements
- Real-time streaming responses (SSE)
- Message editing/deletion
- Conversation search
- Export conversation history
- Conversation sharing between users
- Voice input/output
- File attachments
- Code execution results display
- Conversation branching (multiple paths)

## Testing

### Manual Test Flow
1. Create an agent with web_search tool enabled
2. Navigate to agent detail page
3. Click "Chat" button
4. Send message: "Search for Python tutorials"
5. Agent should respond with formatted search results
6. Send follow-up: "Tell me more about the first result"
7. Verify conversation history is maintained

### API Test
```bash
# 1. Create conversation
CONV_ID=$(curl -s -X POST http://localhost:8000/api/v1/conversations/ \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id"}' | jq -r '.id')

# 2. Send message
curl -X POST http://localhost:8000/api/v1/conversations/$CONV_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, agent!"}'

# 3. View conversation
curl http://localhost:8000/api/v1/conversations/$CONV_ID | jq .
```

## Notes
- System prompts are automatically added as system messages when conversation is created
- Agent execution is async and runs in thread pool
- Frontend auto-scrolls to latest message
- Conversations are tied to specific agents
- Deleting an agent cascades to delete its conversations
- All timestamps are in UTC


