"""
Tool Registry & Schema Generator for Project Jarvis.
Allows Python functions to be registered with @tool and auto-converts docstrings/type annotations
into standard JSON schemas for Ollama and OpenAI tool calling.
"""

import inspect
import json
from typing import Callable, Dict, Any, List, Optional
from core.config import config

class Tool:
    def __init__(self, fn: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.fn = fn
        self.name = name or fn.__name__
        self.description = description or (inspect.getdoc(fn) or "No description provided.").strip()
        self.schema = self._generate_schema()

    def _generate_schema(self) -> Dict[str, Any]:
        """Convert function signature and type hints into JSON Schema."""
        sig = inspect.signature(self.fn)
        properties = {}
        required = []

        type_map = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                param_type = type_map.get(param.annotation, "string")
            
            prop_def: Dict[str, Any] = {"type": param_type}
            
            # Simple docstring extraction for parameter description
            doc = inspect.getdoc(self.fn) or ""
            param_doc = ""
            for line in doc.splitlines():
                if param_name in line and ":" in line:
                    param_doc = line.split(":", 1)[1].strip()
                    break
            if param_doc:
                prop_def["description"] = param_doc
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
            else:
                prop_def["default"] = param.default

            properties[param_name] = prop_def

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def execute(self, **kwargs) -> Any:
        """Execute the tool function with filtered keyword arguments matching signature."""
        try:
            sig = inspect.signature(self.fn)
            # Filter kwargs to only those accepted by the function (unless function accepts **kwargs)
            has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            if not has_var_keyword:
                valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters and v is not None}
            else:
                valid_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return self.fn(**valid_kwargs)
        except Exception as e:
            return f"Error executing tool '{self.name}': {str(e)}"

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, fn: Optional[Callable] = None, name: Optional[str] = None, description: Optional[str] = None):
        """Decorator or direct method to register a tool."""
        def decorator(func: Callable):
            tool = Tool(func, name=name, description=description)
            self._tools[tool.name] = tool
            return func

        if fn is not None:
            return decorator(fn)
        return decorator

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Return list of JSON schemas for all registered tools."""
        return [tool.schema for tool in self._tools.values()]

    def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Find tool by name, execute it, and format result as a clean string."""
        tool = self.get_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found."
        
        print(f"[ToolRegistry] [EXEC] Executing '{tool_name}' with args: {arguments}")
        result = tool.execute(**arguments)
        
        if isinstance(result, (dict, list)):
            return json.dumps(result, indent=2)
        return str(result)

# Global tool registry singleton
registry = ToolRegistry()
tool = registry.register
