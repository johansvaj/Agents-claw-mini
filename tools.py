"""Tool registry for Agents Claw Mini."""

import logging
from typing import Any, Dict, List, Callable, Optional
from dataclasses import dataclass
from .exceptions import ToolException

logger = logging.getLogger("AgentsClawMini.Tools")

@dataclass
class Tool:
    """Represents a registered tool."""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    async_func: bool = False

class ToolRegistry:
    """
    Tool registry untuk pluggable tools.

    Agents bisa menggunakan tools untuk:
    - Web scraping
    - File operations
    - API calls
    - Calculations
    - Database queries
    - Custom functions

    Built-in tools:
    - calculator: Mathematical calculations
    - web_search: Search the web
    - read_file: Read file contents
    - write_file: Write to file
    - fetch_url: Fetch URL content
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in tools."""
        self.register("calculator", "Perform mathematical calculations", self._calculator, {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
            },
            "required": ["expression"]
        })

        self.register("read_file", "Read contents of a file", self._read_file, {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        })

        self.register("write_file", "Write content to a file", self._write_file, {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        })

        self.register("fetch_url", "Fetch content from a URL", self._fetch_url, {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"}
            },
            "required": ["url"]
        }, async_func=True)

    def register(self, name: str, description: str, function: Callable, 
                 parameters: Dict[str, Any], async_func: bool = False):
        """Register a new tool."""
        self._tools[name] = Tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            async_func=async_func
        )
        logger.info("🔧 Tool registered: %s", name)

    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            logger.info("🗑️ Tool unregistered: %s", name)
            return True
        return False

    def get_tool(self, name: str) -> Optional[Callable]:
        """Get tool function by name."""
        tool = self._tools.get(name)
        return tool.function if tool else None

    def has_tool(self, name: str) -> bool:
        """Check if tool exists."""
        return name in self._tools

    def list_tools(self) -> List[str]:
        """List all registered tools."""
        return list(self._tools.keys())

    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool information."""
        tool = self._tools.get(name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "async": tool.async_func
            }
        return None

    def get_all_tools_schema(self) -> List[Dict[str, Any]]:
        """Get schema for all tools (for LLM function calling)."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self._tools.values()
        ]

    # ========== BUILT-IN TOOLS ==========

    def _calculator(self, expression: str) -> str:
        """Calculate mathematical expression."""
        try:
            # Safe evaluation with limited scope
            allowed_names = {
                "abs": abs, "max": max, "min": min,
                "sum": sum, "len": len, "round": round,
                "pow": pow, "divmod": divmod
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    def _read_file(self, path: str) -> str:
        """Read file contents."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error: {e}"

    def _write_file(self, path: str, content: str) -> str:
        """Write content to file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File written: {path}"
        except Exception as e:
            return f"Error: {e}"

    async def _fetch_url(self, url: str) -> str:
        """Fetch URL content."""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as resp:
                    return await resp.text()
        except Exception as e:
            return f"Error: {e}"

    def __repr__(self):
        return f"ToolRegistry(tools={len(self._tools)})"
