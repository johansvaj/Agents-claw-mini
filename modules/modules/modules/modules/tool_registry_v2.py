from typing import Dict, Any, Callable, Awaitable

class ToolRegistryV2:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    def register(self, name: str, func: Callable):
        self.tools[name] = func
    async def execute(self, name: str, args: Dict[str, Any]) -> str:
        if name in self.tools:
            return await self.tools[name](args)
        return f"Tool {name} tidak ditemukan."
