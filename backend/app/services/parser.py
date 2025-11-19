"""Agent definition parser for UI, YAML, and Code formats."""

import yaml
import ast
import json
from typing import Dict, Any
from enum import Enum


class DefinitionType(str, Enum):
    UI = "ui"
    YAML = "yaml"
    CODE = "code"


class AgentParser:
    """Parse agent definitions from different formats into a unified structure."""

    @staticmethod
    def parse(definition_type: str, definition: Any) -> Dict[str, Any]:
        """
        Parse agent definition based on type.
        
        Args:
            definition_type: Type of definition (ui, yaml, code)
            definition: The definition content
            
        Returns:
            Unified agent definition dictionary
        """
        if definition_type == DefinitionType.UI:
            return AgentParser.parse_ui(definition)
        elif definition_type == DefinitionType.YAML:
            return AgentParser.parse_yaml(definition)
        elif definition_type == DefinitionType.CODE:
            return AgentParser.parse_code(definition)
        else:
            raise ValueError(f"Unknown definition type: {definition_type}")

    @staticmethod
    def parse_ui(definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse UI form-based definition.
        
        Expected structure:
        {
            "description": "...",
            "tools": ["tool1", "tool2"],
            "steps": [
                {"action": "...", "tool": "...", "params": {...}}
            ]
        }
        """
        if not isinstance(definition, dict):
            raise ValueError("UI definition must be a dictionary")
        
        # Validate required fields
        if "tools" not in definition:
            definition["tools"] = []
        if "steps" not in definition:
            definition["steps"] = []
        
        # Return normalized definition
        return {
            "type": "ui",
            "description": definition.get("description", ""),
            "tools": definition.get("tools", []),
            "steps": definition.get("steps", []),
            "config": definition.get("config", {})
        }

    @staticmethod
    def parse_yaml(definition: str) -> Dict[str, Any]:
        """
        Parse YAML agent definition.
        
        Expected structure:
        agent:
          name: "Agent Name"
          description: "..."
          tools:
            - tool1
            - tool2
          steps:
            - action: "..."
              tool: "..."
              params: {...}
        """
        if isinstance(definition, dict):
            # Already parsed
            yaml_content = definition
        else:
            try:
                yaml_content = yaml.safe_load(definition)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {str(e)}")
        
        if not isinstance(yaml_content, dict):
            raise ValueError("YAML must contain a dictionary")
        
        # Extract agent definition
        agent_def = yaml_content.get("agent", yaml_content)
        
        return {
            "type": "yaml",
            "description": agent_def.get("description", ""),
            "tools": agent_def.get("tools", []),
            "steps": agent_def.get("steps", []),
            "config": agent_def.get("config", {})
        }

    @staticmethod
    def parse_code(definition: str) -> Dict[str, Any]:
        """
        Parse Python code agent definition.
        
        Expected structure:
        class MyAgent(Agent):
            def run(self, input):
                # Agent logic
                pass
        """
        if isinstance(definition, dict):
            # Already parsed metadata
            return definition
        
        try:
            # Parse Python code using AST
            tree = ast.parse(definition)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python code: {str(e)}")
        
        # Extract class and method information
        agent_class = None
        tools = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                agent_class = node.name
                # Look for tool decorators or attributes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        for decorator in item.decorator_list:
                            if isinstance(decorator, ast.Call):
                                if hasattr(decorator.func, 'id') and decorator.func.id == 'tool':
                                    for arg in decorator.args:
                                        if isinstance(arg, ast.Name):
                                            tools.append(arg.id)
        
        return {
            "type": "code",
            "class_name": agent_class,
            "code": definition,
            "tools": tools,
            "description": f"Python agent class: {agent_class}",
            "steps": [],  # Steps are implicit in code
            "config": {}
        }

    @staticmethod
    def validate(definition: Dict[str, Any]) -> bool:
        """
        Validate a parsed agent definition.
        
        Args:
            definition: Parsed agent definition
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        required_fields = ["type", "tools", "steps"]
        
        for field in required_fields:
            if field not in definition:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(definition["tools"], list):
            raise ValueError("Tools must be a list")
        
        if not isinstance(definition["steps"], list) and definition["type"] != "code":
            raise ValueError("Steps must be a list")
        
        return True

    @staticmethod
    def to_executable(definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parsed definition to executable format.
        
        Args:
            definition: Parsed agent definition
            
        Returns:
            Executable agent configuration
        """
        AgentParser.validate(definition)
        
        executable = {
            "tools": definition["tools"],
            "steps": definition["steps"],
            "config": definition.get("config", {}),
            "type": definition["type"]
        }
        
        if definition["type"] == "code":
            executable["code"] = definition.get("code", "")
            executable["class_name"] = definition.get("class_name", "Agent")
        
        return executable

