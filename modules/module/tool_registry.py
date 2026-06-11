# modules/tool_registry.py
import asyncio
import functools
from typing import Dict, Any, Callable, Awaitable, Optional

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: Optional[str] = None, description: str = "", parameters: dict = None):
        def decorator(func: Callable):
            tool_name = name or func.__name__
            self._tools[tool_name] = {
                "func": func,
                "description": description,
                "parameters": parameters or {"type": "object", "properties": {}}
            }
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    async def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        if name not in self._tools:
            return f"Error: Tool '{name}' not found."
        try:
            result = await self._tools[name]["func"](arguments)
            return str(result)
        except Exception as e:
            return f"Error executing {name}: {e}"

    def get_schema(self) -> list:
        return [{
            "type": "function",
            "function": {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
        } for name, info in self._tools.items()]

    def list_tools(self) -> list:
        return list(self._tools.keys())

_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
        # Register default tools
        @_tool_registry.register("bash", "Execute shell command", {
            "type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]
        })
        async def bash_tool(args):
            proc = await asyncio.create_subprocess_shell(
                args["command"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            return (stdout + stderr).decode()[:3000]

        @_tool_registry.register("read_file", "Read file content", {
            "type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]
        })
        async def read_tool(args):
            import os
            path = os.path.expanduser(args["path"])
            with open(path, 'r') as f:
                return f.read(3000)

        @_tool_registry.register("write_file", "Write content to file", {
            "type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path","content"]
        })
        async def write_tool(args):
            import os
            path = os.path.expanduser(args["path"])
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            with open(path, 'w') as f:
                f.write(args["content"])
            return f"File written: {path}"
    return _tool_registry
