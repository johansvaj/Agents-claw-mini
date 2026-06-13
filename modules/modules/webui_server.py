import asyncio
import threading
import json
from typing import Optional

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

class WebUIServer:
    def __init__(self, agent_engine=None, port=18888):
        self.port = port
        self.agent = agent_engine
        self._thread = None
        self.app = None
        if FASTAPI_AVAILABLE:
            self.app = FastAPI(title="Nexcorix Claw WebUI")
            self._setup_routes()
    def _setup_routes(self):
        @self.app.get("/")
        async def root():
            return HTMLResponse("""
            <html><body><h1>Nexcorix Claw WebUI</h1>
            <div id="chat"></div>
            <input id="msg"><button onclick="send()">Send</button>
            <script>
            let ws = new WebSocket('ws://localhost:18888/ws');
            ws.onmessage = e => document.getElementById('chat').innerHTML += `<div>${e.data}</div>`;
            function send(){ ws.send(document.getElementById('msg').value); }
            </script>
            </body></html>
            """)
        @self.app.websocket("/ws")
        async def ws_endpoint(ws: WebSocket):
            await ws.accept()
            try:
                while True:
                    data = await ws.receive_text()
                    if self.agent:
                        resp = self.agent.process("webui_user", data)
                        await ws.send_text(resp)
                    else:
                        await ws.send_text(f"Echo: {data}")
            except WebSocketDisconnect:
                pass
    def run(self):
        if FASTAPI_AVAILABLE:
            uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="warning")
    def start_background(self):
        if not FASTAPI_AVAILABLE:
            print("[WebUI] FastAPI/uvicorn tidak tersedia. Install: pip install fastapi uvicorn")
            return
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
