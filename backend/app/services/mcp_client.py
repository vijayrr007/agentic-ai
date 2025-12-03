"""MCP (Model Context Protocol) client implementation."""

import subprocess
import json
from typing import Dict, Any, List, Optional
from enum import Enum


class TransportType(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    WEBSOCKET = "websocket"


class MCPClient:
    """Client for communicating with MCP servers."""

    def __init__(self, server_config: Dict[str, Any]):
        """
        Initialize MCP client.
        
        Args:
            server_config: Server configuration including transport and connection details
        """
        self.config = server_config
        self.transport = server_config.get("transport", TransportType.STDIO)
        self.process = None
        self.connected = False

    async def connect(self) -> bool:
        """
        Connect to the MCP server.
        
        Returns:
            True if connection successful
        """
        if self.transport == TransportType.STDIO:
            return self._connect_stdio()
        elif self.transport == TransportType.SSE:
            return await self._connect_sse()
        elif self.transport == TransportType.WEBSOCKET:
            return await self._connect_websocket()
        else:
            raise ValueError(f"Unsupported transport: {self.transport}")

    def _connect_stdio(self) -> bool:
        """Connect to MCP server using stdio transport."""
        try:
            command = self.config.get("command")
            args = self.config.get("args", [])
            env = self.config.get("env", {})
            
            if not command:
                raise ValueError("Command is required for stdio transport")
            
            # Start the MCP server process
            full_command = [command] + args
            
            self.process = subprocess.Popen(
                full_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**subprocess.os.environ, **env}
            )
            
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect via stdio: {str(e)}")
            return False

    async def _connect_sse(self) -> bool:
        """Connect to MCP server using SSE transport."""
        # TODO: Implement SSE connection
        print("SSE transport not yet implemented")
        return False

    async def _connect_websocket(self) -> bool:
        """Connect to MCP server using WebSocket transport."""
        # TODO: Implement WebSocket connection
        print("WebSocket transport not yet implemented")
        return False

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        self.connected = False

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Returns:
            List of tool definitions
        """
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        # Send tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._send_request(request)
        
        if response and "result" in response:
            return response["result"].get("tools", [])
        return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a specific tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            raise RuntimeError(f"Tool call failed: {response['error']}")
        
        return None

    async def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a JSON-RPC request to the MCP server.
        
        Args:
            request: JSON-RPC request
            
        Returns:
            JSON-RPC response
        """
        if self.transport == TransportType.STDIO and self.process:
            try:
                # Send request
                request_json = json.dumps(request) + "\n"
                self.process.stdin.write(request_json)
                self.process.stdin.flush()
                
                # Read response
                response_line = self.process.stdout.readline()
                if response_line:
                    return json.loads(response_line)
            except Exception as e:
                print(f"Error sending request: {str(e)}")
                return None
        
        return None


class BuiltInTools:
    """Built-in MCP tools that don't require external servers."""

    @staticmethod
    async def file_read(path: str) -> str:
        """Read a file from disk."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {str(e)}")

    @staticmethod
    async def file_write(path: str, content: str) -> bool:
        """Write content to a file."""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to write file: {str(e)}")

    @staticmethod
    async def file_list(directory: str) -> List[str]:
        """List files in a directory."""
        try:
            import os
            return os.listdir(directory)
        except Exception as e:
            raise RuntimeError(f"Failed to list directory: {str(e)}")

    @staticmethod
    async def http_request(url: str, method: str = "GET", body: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an HTTP request."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=body)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=body)
                elif method.upper() == "DELETE":
                    response = await client.delete(url)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text
                }
        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {str(e)}")

    @staticmethod
    async def web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using DuckDuckGo HTML scraping (more reliable)."""
        try:
            import httpx
            from bs4 import BeautifulSoup
            import urllib.parse
            
            # Encode the query
            encoded_query = urllib.parse.quote_plus(query)
            
            # DuckDuckGo HTML search URL
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Set up headers to mimic a browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            # Make the request
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                results = []
                
                # Find search result divs
                search_results = soup.find_all('div', class_='result')
                
                for result in search_results[:max_results]:
                    try:
                        # Extract title
                        title_elem = result.find('a', class_='result__a')
                        title = title_elem.get_text(strip=True) if title_elem else "No title"
                        
                        # Extract URL
                        url_elem = result.find('a', class_='result__url')
                        result_url = url_elem.get('href') if url_elem else ""
                        if not result_url.startswith('http'):
                            # Handle relative URLs
                            result_url = f"https://{result_url}" if result_url else ""
                        
                        # Extract snippet
                        snippet_elem = result.find('a', class_='result__snippet')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description available"
                        
                        results.append({
                            "title": title,
                            "url": result_url,
                            "snippet": snippet
                        })
                        
                        if len(results) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error parsing search result: {e}")
                        continue
                
                if not results:
                    # Return a helpful message if no results found
                    return [{
                        "title": "No results found",
                        "url": "",
                        "snippet": f"Could not find any results for '{query}'. The search service may be temporarily unavailable."
                    }]
                
                return results
                
        except Exception as e:
            import traceback
            print(f"Web search error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # Return error as a result instead of raising
            return [{
                "title": "Search Error",
                "url": "",
                "snippet": f"Web search encountered an error: {str(e)}. Please try again later."
            }]
    
    @staticmethod
    async def llm_query(prompt: str, system_prompt: str = None, model: str = "gpt-3.5-turbo", max_tokens: int = 500) -> Dict[str, Any]:
        """
        Query an LLM (OpenAI) for intelligent responses.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system prompt to guide the LLM
            model: OpenAI model to use (default: gpt-3.5-turbo)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict with response and metadata
        """
        try:
            from openai import OpenAI
            from app.core.config import settings
            
            if not settings.OPENAI_API_KEY:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured. Please add OPENAI_API_KEY to .env file."
                }
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Call OpenAI
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": response.model,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
            
        except Exception as e:
            import traceback
            print(f"LLM query error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"LLM query failed: {str(e)}"
            }

