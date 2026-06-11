import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

class WebUI:
    def __init__(self, message_bus=None, port=18888):
        self.port = port
        self.bus = message_bus
        self.app = FastAPI()
        self._thread = None
        self._setup()
    def _setup(self):
        @self.app.get("/")
        async def root():
            return HTMLResponse("""<html><body><h1>Nexcorix Claw WebUI</h1><div id="chat"></div><input id="msg"><button onclick="send()">Send</button><script>let ws=new WebSocket('/ws');ws.onmessage=e=>document.getElementById('chat').innerHTML+=`<div>${e.data}</div>`;function send(){ws.send(document.getElementById('msg').value)}</script></body></html>""")
        @self.app.websocket("/ws")
        async def ws(websocket):
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    await websocket.send_text(f"Echo: {data}")
            except WebSocketDisconnect:
                pass
    def run(self):
        uvicorn.run(self.app, host="127.0.0.1", port=self.port)
    def start_background(self):
        if not self._thread or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run, daemon=True)
            self._thread.start()
