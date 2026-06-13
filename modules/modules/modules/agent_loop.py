import asyncio
import json
from typing import Dict, Any
from .message_bus import InboundMessage, OutboundMessage
from .llm_provider import LLMProvider
from .tool_registry_v2 import ToolRegistryV2
from .advanced_memory import AdvancedMemory
from .workspace_v2 import WorkspaceV2
from .skill_loader import SkillLoader

class AgentLoop:
    def __init__(self, bus, llm: LLMProvider, memory: AdvancedMemory, workspace: WorkspaceV2, skills: SkillLoader):
        self.bus = bus
        self.llm = llm
        self.memory = memory
        self.workspace = workspace
        self.skills = skills
        self.tool_registry = ToolRegistryV2()
        self._running = True

    async def run(self):
        while self._running:
            msg = await self.bus.get_inbound()
            asyncio.create_task(self._process(msg))

    async def _process(self, msg: InboundMessage):
        # Bangun konteks dari workspace + memori
        system_prompt = self.workspace.build_system_prompt()
        # Tambahkan memori relevan
        memories = self.memory.search(msg.content, user_id=msg.user_id)
        if memories:
            system_prompt += "\n\n## Memori relevan\n" + "\n".join(memories)
        # Tambahkan skill yang tersedia
        skills_desc = self.skills.list_skills()
        if skills_desc:
            system_prompt += "\n\n## Skills tersedia\n" + "\n".join([f"- {s['name']}: {s['description']}" for s in skills_desc])
        # History percakapan sederhana (bisa disimpan di memory)
        # Kirim ke LLM
        user_msg = msg.content
        llm_response = await self.llm.chat(user_msg, system_prompt)
        # Simpan ke memori
        self.memory.add(f"User: {user_msg}", user_id=msg.user_id)
        self.memory.add(f"Assistant: {llm_response}", user_id=msg.user_id)
        # Kirim balasan
        out = OutboundMessage(content=llm_response, recipient_id=msg.sender_id, channel=msg.channel)
        await self.bus.publish_outbound(out)

    def handle_user_message(self, user_id, text):
        # Untuk penggunaan langsung (non-async)
        # Simulasi sinkron
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        msg = InboundMessage(content=text, sender_id=user_id, channel="cli", user_id=user_id)
        response = loop.run_until_complete(self._process_sync(msg))
        loop.close()
        return response

    async def _process_sync(self, msg: InboundMessage):
        system_prompt = self.workspace.build_system_prompt()
        return await self.llm.chat(msg.content, system_prompt)
