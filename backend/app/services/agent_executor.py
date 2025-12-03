"""Agent execution engine using subprocess isolation."""

import subprocess
import tempfile
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from app.services.mcp_client import BuiltInTools


class AgentExecutor:
    """Execute agents in isolated Python processes."""

    def __init__(self, agent_definition: Dict[str, Any], workspace_dir: Optional[str] = None, callback=None):
        """
        Initialize the agent executor.
        
        Args:
            agent_definition: Parsed agent definition
            workspace_dir: Optional workspace directory for file operations
            callback: Optional callback function for streaming updates
        """
        self.definition = agent_definition
        self.workspace_dir = workspace_dir or tempfile.mkdtemp()
        self.execution_logs = []
        self.callback = callback

    def execute(self, inputs: Optional[Dict[str, Any]] = None, timeout: int = 300) -> Dict[str, Any]:
        """
        Execute the agent.
        
        Args:
            inputs: Input parameters for the agent
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result with logs and output
        """
        inputs = inputs or {}
        
        try:
            if self.definition["type"] == "code":
                return self._execute_code(inputs, timeout)
            else:
                return self._execute_steps(inputs, timeout)
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": f"Execution timed out after {timeout} seconds",
                "logs": "\n".join(self.execution_logs)
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "logs": "\n".join(self.execution_logs)
            }

    def _execute_code(self, inputs: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Execute code-based agent definition."""
        self._log("Starting code execution...")
        
        # Create temporary Python file with agent code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write the agent code
            f.write(self.definition.get("code", ""))
            f.write("\n\n")
            # Add execution wrapper
            f.write(f"""
if __name__ == "__main__":
    import json
    inputs = {json.dumps(inputs)}
    agent = {self.definition.get('class_name', 'Agent')}()
    try:
        result = agent.run(inputs)
        print(json.dumps({{"status": "success", "result": result}}))
    except Exception as e:
        print(json.dumps({{"status": "error", "error": str(e)}}))
""")
            temp_file = f.name
        
        try:
            # Execute the Python file in a subprocess
            result = subprocess.run(
                ["python3", temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace_dir
            )
            
            self._log(f"Exit code: {result.returncode}")
            self._log(f"stdout: {result.stdout}")
            
            if result.stderr:
                self._log(f"stderr: {result.stderr}")
            
            # Parse the output
            try:
                output = json.loads(result.stdout.strip().split('\n')[-1])
                return {
                    "status": "completed" if output.get("status") == "success" else "failed",
                    "result": output.get("result"),
                    "error": output.get("error"),
                    "logs": "\n".join(self.execution_logs)
                }
            except json.JSONDecodeError:
                return {
                    "status": "completed",
                    "result": result.stdout,
                    "logs": "\n".join(self.execution_logs)
                }
        finally:
            # Clean up temp file
            os.unlink(temp_file)

    def _execute_steps(self, inputs: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Execute step-based agent definition."""
        self._log("Starting step-based execution...")
        
        results = {}
        context = {"input": inputs}
        
        for i, step in enumerate(self.definition.get("steps", [])):
            step_num = i + 1
            self._log(f"Executing step {step_num}: {step.get('action', 'unknown')}")
            
            try:
                # Execute the step
                step_result = self._execute_step(step, context, timeout)
                results[f"step{step_num}"] = step_result
                context[f"step{step_num}"] = step_result
                
                self._log(f"Step {step_num} completed successfully")
            except Exception as e:
                self._log(f"Step {step_num} failed: {str(e)}")
                return {
                    "status": "failed",
                    "error": f"Step {step_num} failed: {str(e)}",
                    "results": results,
                    "logs": "\n".join(self.execution_logs)
                }
        
        return {
            "status": "completed",
            "results": results,
            "logs": "\n".join(self.execution_logs)
        }

    def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any], timeout: int) -> Any:
        """
        Execute a single step.
        
        Args:
            step: Step definition
            context: Execution context with previous results
            timeout: Step timeout
            
        Returns:
            Step execution result
        """
        tool = step.get("tool")
        params = step.get("params", {})
        
        # Resolve parameter references (e.g., {input.query} or {step1.output})
        resolved_params = self._resolve_params(params, context)
        
        self._log(f"Calling tool '{tool}' with params: {resolved_params}")
        
        # Execute the actual tool
        try:
            result = asyncio.run(self._call_tool(tool, resolved_params))
            self._log(f"Tool '{tool}' executed successfully")
            
            # Stream tool result to callback if provided
            if self.callback:
                try:
                    self.callback("tool_result", result)
                except Exception:
                    pass
            
            return result
        except Exception as e:
            self._log(f"Tool '{tool}' failed: {str(e)}")
            raise
    
    async def _call_tool(self, tool: str, params: Dict[str, Any]) -> Any:
        """
        Call the appropriate tool with given parameters.
        
        Args:
            tool: Tool name
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        if tool == "web_search":
            query = params.get("query", "")
            max_results = params.get("max_results", 5)
            results = await BuiltInTools.web_search(query, max_results)
            return {
                "tool": "web_search",
                "query": query,
                "results": results,
                "count": len(results),
                "executed_at": datetime.utcnow().isoformat()
            }
        
        elif tool == "file_read":
            path = params.get("path", "")
            content = await BuiltInTools.file_read(path)
            return {
                "tool": "file_read",
                "path": path,
                "content": content,
                "executed_at": datetime.utcnow().isoformat()
            }
        
        elif tool == "file_write":
            path = params.get("path", "")
            content = params.get("content", "")
            await BuiltInTools.file_write(path, content)
            return {
                "tool": "file_write",
                "path": path,
                "success": True,
                "executed_at": datetime.utcnow().isoformat()
            }
        
        elif tool == "http_request":
            url = params.get("url", "")
            method = params.get("method", "GET")
            body = params.get("body")
            result = await BuiltInTools.http_request(url, method, body)
            return {
                "tool": "http_request",
                "url": url,
                "method": method,
                "response": result,
                "executed_at": datetime.utcnow().isoformat()
            }
        
        elif tool == "llm_query":
            prompt = params.get("prompt", "")
            system_prompt = params.get("system_prompt")
            model = params.get("model", "gpt-3.5-turbo")
            max_tokens = params.get("max_tokens", 500)
            result = await BuiltInTools.llm_query(prompt, system_prompt, model, max_tokens)
            return {
                "tool": "llm_query",
                "prompt": prompt,
                "result": result,
                "executed_at": datetime.utcnow().isoformat()
            }
        
        else:
            raise ValueError(f"Unknown tool: {tool}")

    def _resolve_params(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve parameter references in the context.
        
        Args:
            params: Parameters with potential references
            context: Execution context
            
        Returns:
            Resolved parameters
        """
        import re
        import json
        
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str):
                # Check if it's a simple reference like {input.query}
                if value.startswith("{") and value.endswith("}") and "{" not in value[1:-1]:
                    # Extract reference path (e.g., "input.query" from "{input.query}")
                    ref_path = value[1:-1].split(".")
                    
                    # Navigate context to get value
                    current = context
                    try:
                        for part in ref_path:
                            current = current[part]
                        resolved[key] = current
                    except (KeyError, TypeError):
                        resolved[key] = value  # Keep original if reference not found
                else:
                    # Handle string interpolation with multiple references
                    result = value
                    # Find all {xxx.yyy} patterns
                    for match in re.finditer(r'\{([^}]+)\}', value):
                        ref = match.group(1)
                        ref_path = ref.split(".")
                        
                        # Navigate context to get value
                        current = context
                        try:
                            for part in ref_path:
                                current = current[part]
                            # Convert to string (JSON for complex objects)
                            if isinstance(current, (dict, list)):
                                replacement = json.dumps(current, indent=2)
                            else:
                                replacement = str(current)
                            result = result.replace(match.group(0), replacement)
                        except (KeyError, TypeError):
                            pass  # Keep original if reference not found
                    
                    resolved[key] = result
            else:
                resolved[key] = value
        
        return resolved

    def _log(self, message: str):
        """Add a message to execution logs."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_logs.append(log_entry)
        
        # Stream log to callback if provided
        if self.callback:
            try:
                self.callback("log", log_entry)
            except Exception:
                pass  # Don't let callback errors break execution

