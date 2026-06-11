# modules/mcp_client.py
import json
import asyncio
from typing import Dict, Any, Optional

try:
    import httpx
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

class MCPClient:
    def __init__(self, server_url: str = None):
        self.server_url = server_url
        self.session = None
        self.available = MCP_AVAILABLE and server_url is not None

    async def connect(self):
        if not self.available: return
        self.session = httpx.AsyncClient(timeout=30)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        if not self.available or not self.session:
            return None
        try:
            resp = await self.session.post(
                f"{self.server_url}/tools/{tool_name}",
                json=arguments
            )
            return resp.text
        except Exception as e:
            return f"MCP error: {e}"

    async def close(self):
        if self.session:
            await self.session.aclose()
