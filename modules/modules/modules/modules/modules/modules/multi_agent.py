from typing import Dict, Any

class SpecialistAgent:
    def __init__(self, name: str, system_prompt: str, parent_engine):
        self.name = name
        self.prompt = system_prompt
        self.engine = parent_engine
    async def process(self, task: str) -> str:
        success, resp = self.engine.chat_with_ai(f"agent_{self.name}", task, system_prompt=self.prompt)
        return resp if success else f"[{self.name}] Error: {resp}"

class MultiAgentOrchestrator:
    def __init__(self, main_engine):
        self.main = main_engine
        self.agents: Dict[str, SpecialistAgent] = {}
    def register_agent(self, name: str, prompt: str):
        self.agents[name] = SpecialistAgent(name, prompt, self.main)
    async def delegate(self, task: str, agent_name: str) -> str:
        if agent_name not in self.agents:
            return f"Agent '{agent_name}' not found."
        return await self.agents[agent_name].process(task)
