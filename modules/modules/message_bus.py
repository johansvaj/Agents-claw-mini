import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class InboundMessage:
    content: str
    sender_id: str
    channel: str
    user_id: Optional[str] = None

@dataclass
class OutboundMessage:
    content: str
    recipient_id: str
    channel: str

class MessageBus:
    def __init__(self):
        self.inbound_queue = asyncio.Queue()
        self.outbound_queue = asyncio.Queue()
    async def publish_inbound(self, msg: InboundMessage):
        await self.inbound_queue.put(msg)
    async def get_inbound(self) -> InboundMessage:
        return await self.inbound_queue.get()
    async def publish_outbound(self, msg: OutboundMessage):
        await self.outbound_queue.put(msg)
    async def get_outbound(self) -> OutboundMessage:
        return await self.outbound_queue.get()
