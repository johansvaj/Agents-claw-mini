import asyncio
from datetime import datetime, timedelta
from .memory_store import MemoryStore

class MemoryCompactor:
    def __init__(self, memory_store: MemoryStore, llm_provider, interval_minutes: int = 60):
        self.memory = memory_store
        self.llm = llm_provider
        self.interval = interval_minutes
        self.last_run = datetime.now()
    async def run(self):
        while True:
            await asyncio.sleep(self.interval * 60)
            if datetime.now() - self.last_run < timedelta(minutes=self.interval):
                continue
            await self.compact()
            self.last_run = datetime.now()
    async def compact(self):
        # Ambil memori lama (lebih dari 7 hari) → di sini sederhana, ambil 50 terbaru dan ringkas
        old = self.memory.get_recent(50)
        if not old:
            return
        prompt = f"Ringkas poin-poin penting dari percakapan berikut:\n" + "\n".join(old[:20])
        success, summary = await self.llm.generate([{"role": "user", "content": prompt}], [])
        if success and summary:
            self.memory.add(f"[Ringkasan] {summary[:500]}")
