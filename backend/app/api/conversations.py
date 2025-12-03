from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.agent import Agent
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    MessageResponse
)
from app.services.agent_executor import AgentExecutor

router = APIRouter()


@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    agent_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all conversations with optional filtering by agent."""
    query = db.query(Conversation)
    
    if agent_id:
        query = query.filter(Conversation.agent_id == agent_id)
    
    total = query.count()
    conversations = query.order_by(Conversation.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return ConversationListResponse(
        conversations=conversations,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    # Verify agent exists
    agent = db.query(Agent).filter(Agent.id == conversation_data.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Auto-generate title if not provided
    title = conversation_data.title or f"Chat with {agent.name}"
    
    conversation = Conversation(
        agent_id=conversation_data.agent_id,
        title=title
    )
    
    # Add system message if agent has system prompt
    if agent.system_prompt:
        system_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.system,
            content=agent.system_prompt
        )
        conversation.messages.append(system_message)
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation with all messages."""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    conversation_id: str,
    message_data: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """Send a message and get agent response."""
    # Get conversation
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get agent
    agent = db.query(Agent).filter(Agent.id == conversation.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.user,
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Build conversation history for context
    conversation_history = []
    for msg in conversation.messages:
        conversation_history.append({
            "role": msg.role.value,
            "content": msg.content
        })
    
    # Format conversation history as a readable string for LLM context
    history_text = ""
    if conversation_history:
        history_lines = []
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            role = msg["role"].capitalize()
            content = msg["content"]
            # Truncate very long messages
            if len(content) > 500:
                content = content[:500] + "..."
            history_lines.append(f"{role}: {content}")
        history_text = "\n".join(history_lines)
    
    # Prepare agent definition
    agent_definition = {
        "type": agent.definition_type.value if hasattr(agent.definition_type, 'value') else str(agent.definition_type),
        "tools": agent.definition.get("tools", []),
        "steps": []
    }
    
    # Create intelligent workflow steps based on agent tools
    steps = []
    
    if "web_search" in agent_definition["tools"]:
        # Step 1: Search the web
        steps.append({
            "action": "search_web",
            "tool": "web_search",
            "params": {
                "query": message_data.content,
                "max_results": 5
            }
        })
        
        # Build the LLM prompt with conversation history
        llm_prompt = f"""Previous conversation:
{history_text if history_text else "(No previous messages)"}

Current user question: {message_data.content}

Search results for this question: {{step1.results}}

Instructions:
- Consider the conversation history when responding
- If the user is asking a follow-up question, relate your answer to previous messages
- Provide a helpful, natural language response based on the search results
- Synthesize the information and cite sources when relevant
- If the search results don't answer the question, say so honestly"""
        
        # Step 2: Use LLM to analyze and respond with search results
        steps.append({
            "action": "analyze_with_llm",
            "tool": "llm_query",
            "params": {
                "prompt": llm_prompt,
                "system_prompt": agent.system_prompt or "You are a helpful AI assistant with memory of the conversation. You analyze web search results and provide clear, contextual responses based on the conversation history.",
                "max_tokens": 600
            }
        })
    
    agent_definition["steps"] = steps
    
    # Execute agent
    try:
        executor = AgentExecutor(agent_definition)
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool,
                lambda: executor.execute(inputs={"message": message_data.content, "history": conversation_history})
            )
        
        # Generate assistant response from execution result
        if result["status"] == "completed":
            # Format the response based on tool results
            response_content = format_agent_response(result)
        else:
            response_content = f"I encountered an error: {result.get('error', 'Unknown error')}"
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.assistant,
            content=response_content
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(assistant_message)
        
        return ChatMessageResponse(
            message=MessageResponse.model_validate(user_message),
            assistant_message=MessageResponse.model_validate(assistant_message)
        )
        
    except Exception as e:
        # Save error as assistant message
        error_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.assistant,
            content=f"I'm sorry, I encountered an error: {str(e)}"
        )
        db.add(error_message)
        db.commit()
        db.refresh(error_message)
        
        return ChatMessageResponse(
            message=MessageResponse.model_validate(user_message),
            assistant_message=MessageResponse.model_validate(error_message)
        )


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation."""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    return None


def format_agent_response(result: dict) -> str:
    """Format agent execution result into a readable response."""
    if result.get("results"):
        # Handle step-based results
        steps_results = result["results"]
        
        # Check if we have an LLM response (priority)
        for step_key, step_result in steps_results.items():
            tool = step_result.get("tool")
            if tool == "llm_query":
                llm_result = step_result.get("result", {})
                if llm_result.get("success"):
                    # Return the LLM's natural language response directly
                    return llm_result.get("response", "No response generated.")
                else:
                    # LLM failed, fall back to manual formatting
                    error = llm_result.get("error", "Unknown error")
                    print(f"LLM query failed: {error}")
                    # Continue to manual formatting below
                    break
        
        # Manual formatting for non-LLM or failed LLM responses
        response_parts = []
        
        for step_key, step_result in steps_results.items():
            tool = step_result.get("tool")
            
            if tool == "web_search":
                query = step_result.get("query", "")
                search_results = step_result.get("results", [])
                
                if search_results:
                    response_parts.append(f"I searched for '{query}' and found {len(search_results)} results:")
                    for i, result_item in enumerate(search_results[:5], 1):
                        title = result_item.get("title", "No title")
                        url = result_item.get("url", "")
                        snippet = result_item.get("snippet", "")
                        response_parts.append(f"\n{i}. **{title}**")
                        if snippet:
                            response_parts.append(f"   {snippet}")
                        if url:
                            response_parts.append(f"   Link: {url}")
                else:
                    response_parts.append(f"I searched for '{query}' but didn't find any results.")
            
            elif tool == "file_read":
                path = step_result.get("path", "")
                content = step_result.get("content", "")
                response_parts.append(f"I read the file '{path}':\n```\n{content[:500]}\n```")
            
            elif tool == "file_write":
                path = step_result.get("path", "")
                response_parts.append(f"I saved the content to '{path}'.")
            
            elif tool == "http_request":
                url = step_result.get("url", "")
                response_data = step_result.get("response", {})
                status_code = response_data.get("status_code", "")
                response_parts.append(f"I made a request to {url} (Status: {status_code}).")
        
        return "\n\n".join(response_parts) if response_parts else "Task completed successfully."
    
    elif result.get("result"):
        # Handle direct results
        return str(result["result"])
    
    return "Task completed."

