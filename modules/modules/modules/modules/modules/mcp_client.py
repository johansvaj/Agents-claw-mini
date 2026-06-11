import asyncio
try:
    import httpx
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

class MCPClient:
    def __init__(self, server_url: str = None):
        self.url = server_url
        self.available = MCP_AVAILABLE and self.url is not None
        self.client = None
    async def connect(self):
        if self.available:
            self.client = httpx.AsyncClient(timeout=30)
    async def call_tool(self, tool_name: str, args: dict):
        if not self.available or not self.client:
            return "MCP not available"
        try:
            resp = await self.client.post(f"{self.url}/tools/{tool_name}", json=args)
            return resp.text
        except Exception as e:
            return f"MCP error: {e}"
    async def close(self):
        if self.client:
            await self.client.aclose()
