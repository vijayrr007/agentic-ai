"""Agent execution engine using subprocess isolation."""

import subprocess
import tempfile
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class AgentExecutor:
    """Execute agents in isolated Python processes."""

    def __init__(self, agent_definition: Dict[str, Any], workspace_dir: Optional[str] = None):
        """
        Initialize the agent executor.
        
        Args:
            agent_definition: Parsed agent definition
            workspace_dir: Optional workspace directory for file operations
        """
        self.definition = agent_definition
        self.workspace_dir = workspace_dir or tempfile.mkdtemp()
        self.execution_logs = []

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
        
        # For now, simulate tool execution
        # TODO: Integrate with actual MCP tool execution
        self._log(f"Calling tool '{tool}' with params: {resolved_params}")
        
        # Placeholder for tool execution
        result = {
            "tool": tool,
            "params": resolved_params,
            "output": f"Simulated output from {tool}",
            "executed_at": datetime.utcnow().isoformat()
        }
        
        return result

    def _resolve_params(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve parameter references in the context.
        
        Args:
            params: Parameters with potential references
            context: Execution context
            
        Returns:
            Resolved parameters
        """
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
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
                resolved[key] = value
        
        return resolved

    def _log(self, message: str):
        """Add a message to execution logs."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_logs.append(log_entry)

