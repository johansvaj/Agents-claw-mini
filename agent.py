"""AI Agent implementation for Agents Claw Mini."""

import json
import asyncio
import logging
import aiohttp
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from .config import LLMConfig, PROVIDER_CONFIGS
from .memory import Memory
from .tools import ToolRegistry
from .sandbox import Sandbox
from .exceptions import AgentException, LLMException

logger = logging.getLogger("AgentsClawMini.Agent")

@dataclass
class Message:
    """Represents a chat message."""
    role: str  # system, user, assistant, tool
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

@dataclass
class AgentResponse:
    """Response from agent."""
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)
    model: str = ""
    provider: str = ""
    latency_ms: float = 0.0

class Agent:
    """
    AI Agent dengan multi-LLM support.

    Mendukung 9+ provider:
    - OpenAI, Anthropic, Google, Mistral, Cohere
    - Groq, DeepSeek, Ollama, OpenRouter

    Features:
    - Chat dengan history
    - Tool calling
    - Memory persistence
    - Streaming response
    - Sandbox execution
    """

    def __init__(self, name: str, config: LLMConfig, 
                 system_prompt: Optional[str] = None,
                 tools: Optional[List[str]] = None,
                 memory: Optional[Memory] = None,
                 tool_registry: Optional[ToolRegistry] = None,
                 sandbox: Optional[Sandbox] = None):
        self.name = name
        self.config = config
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.tools = tools or []
        self.memory = memory
        self.tool_registry = tool_registry
        self.sandbox = sandbox

        self._history: List[Message] = []
        self._session: Optional[aiohttp.ClientSession] = None

        # Add system prompt
        self._history.append(Message(role="system", content=self.system_prompt))

        logger.info("🤖 Agent '%s' ready | Provider: %s | Model: %s", 
                   name, config.provider, config.model)

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self._session

    # ========== CHAT METHODS ==========

    async def chat(self, message: str, stream: bool = False) -> Union[AgentResponse, Any]:
        """Send a chat message and get response."""
        # Add user message to history
        self._history.append(Message(role="user", content=message))

        # Save to memory if available
        if self.memory:
            await self.memory.add("chat", {"role": "user", "content": message, "agent": self.name})

        # Call LLM
        if stream:
            return await self._stream_chat()

        response = await self._call_llm()

        # Add assistant response to history
        self._history.append(Message(role="assistant", content=response.content))

        # Save to memory
        if self.memory:
            await self.memory.add("chat", {"role": "assistant", "content": response.content, "agent": self.name})

        # Execute tool calls if any
        if response.tool_calls and self.tool_registry:
            tool_results = await self._execute_tools(response.tool_calls)
            # Add tool results to history and get final response
            for result in tool_results:
                self._history.append(Message(role="tool", content=str(result)))

            final_response = await self._call_llm()
            return final_response

        return response

    async def _call_llm(self) -> AgentResponse:
        """Call LLM API based on provider."""
        import time
        start_time = time.time()

        provider = self.config.provider

        try:
            if provider == "openai":
                response = await self._call_openai()
            elif provider == "anthropic":
                response = await self._call_anthropic()
            elif provider == "google":
                response = await self._call_google()
            elif provider == "mistral":
                response = await self._call_mistral()
            elif provider == "cohere":
                response = await self._call_cohere()
            elif provider == "groq":
                response = await self._call_groq()
            elif provider == "deepseek":
                response = await self._call_deepseek()
            elif provider == "ollama":
                response = await self._call_ollama()
            elif provider == "openrouter":
                response = await self._call_openrouter()
            else:
                raise LLMException(f"Provider '{provider}' tidak didukung")

            latency = (time.time() - start_time) * 1000
            response.latency_ms = latency
            response.provider = provider

            logger.info("💬 Response dari %s (%s) | Latency: %.0fms", 
                       provider, response.model, latency)

            return response

        except Exception as e:
            raise LLMException(f"Gagal memanggil LLM ({provider}): {e}")

    # ========== OPENAI ==========
    async def _call_openai(self) -> AgentResponse:
        """Call OpenAI API."""
        messages = [msg.to_dict() for msg in self._history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "frequency_penalty": self.config.frequency_penalty,
            "presence_penalty": self.config.presence_penalty,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        async with self.session.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"OpenAI error: {data}")

            choice = data["choices"][0]
            content = choice["message"].get("content", "")
            tool_calls = choice["message"].get("tool_calls", [])

            return AgentResponse(
                content=content,
                tool_calls=tool_calls,
                usage=data.get("usage", {}),
                model=data.get("model", self.config.model),
            )

    # ========== ANTHROPIC ==========
    async def _call_anthropic(self) -> AgentResponse:
        """Call Anthropic Claude API."""
        messages = []
        system = None
        for msg in self._history:
            if msg.role == "system":
                system = msg.content
            else:
                messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }
        if system:
            payload["system"] = system

        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        async with self.session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        ) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"Anthropic error: {data}")

            content = ""
            for block in data.get("content", []):
                if block["type"] == "text":
                    content += block["text"]

            return AgentResponse(
                content=content,
                usage=data.get("usage", {}),
                model=data.get("model", self.config.model),
            )

    # ========== GOOGLE ==========
    async def _call_google(self) -> AgentResponse:
        """Call Google Gemini API."""
        contents = []
        for msg in self._history:
            if msg.role != "system":
                role = "user" if msg.role == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg.content}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens,
                "topP": self.config.top_p,
            }
        }

        url = f"{self.config.base_url}/v1beta/models/{self.config.model}:generateContent?key={self.config.api_key}"

        async with self.session.post(url, json=payload) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"Google error: {data}")

            content = ""
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    content += part.get("text", "")

            return AgentResponse(
                content=content,
                model=self.config.model,
            )

    # ========== MISTRAL ==========
    async def _call_mistral(self) -> AgentResponse:
        """Call Mistral API."""
        messages = [msg.to_dict() for msg in self._history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        async with self.session.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"Mistral error: {data}")

            choice = data["choices"][0]
            return AgentResponse(
                content=choice["message"].get("content", ""),
                usage=data.get("usage", {}),
                model=data.get("model", self.config.model),
            )

    # ========== COHERE ==========
    async def _call_cohere(self) -> AgentResponse:
        """Call Cohere API."""
        messages = []
        preamble = None
        for msg in self._history:
            if msg.role == "system":
                preamble = msg.content
            else:
                messages.append({"role": msg.role, "message": msg.content})

        payload = {
            "model": self.config.model,
            "message": messages[-1]["message"] if messages else "",
            "chat_history": messages[:-1] if len(messages) > 1 else [],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if preamble:
            payload["preamble"] = preamble

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        async with self.session.post(
            "https://api.cohere.com/v1/chat",
            headers=headers,
            json=payload
        ) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"Cohere error: {data}")

            return AgentResponse(
                content=data.get("text", ""),
                model=self.config.model,
            )

    # ========== GROQ ==========
    async def _call_groq(self) -> AgentResponse:
        """Call Groq API (super fast inference)."""
        messages = [msg.to_dict() for msg in self._history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        async with self.session.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"Groq error: {data}")

            choice = data["choices"][0]
            return AgentResponse(
                content=choice["message"].get("content", ""),
                usage=data.get("usage", {}),
                model=data.get("model", self.config.model),
            )

    # ========== DEEPSEEK ==========
    async def _call_deepseek(self) -> AgentResponse:
        """Call DeepSeek API."""
        messages = [msg.to_dict() for msg in self._history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        async with self.session.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"DeepSeek error: {data}")

            choice = data["choices"][0]
            return AgentResponse(
                content=choice["message"].get("content", ""),
                usage=data.get("usage", {}),
                model=data.get("model", self.config.model),
            )

    # ========== OLLAMA (Local) ==========
    async def _call_ollama(self) -> AgentResponse:
        """Call Ollama API (local models)."""
        messages = [msg.to_dict() for msg in self._history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            }
        }

        async with self.session.post(
            f"{self.config.base_url}/api/chat",
            json=payload
        ) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"Ollama error: {data}")

            return AgentResponse(
                content=data.get("message", {}).get("content", ""),
                model=self.config.model,
            )

    # ========== OPENROUTER (100+ Models) ==========
    async def _call_openrouter(self) -> AgentResponse:
        """
        Call OpenRouter API - akses ke 100+ model!

        Model format: "provider/model-name"
        Contoh: "openai/gpt-4o", "anthropic/claude-3.5-sonnet", 
                "meta-llama/llama-3.1-70b-instruct"
        """
        messages = [msg.to_dict() for msg in self._history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agents-claw-mini.dev",  # Required by OpenRouter
            "X-Title": "Agents Claw Mini",  # Required by OpenRouter
        }

        async with self.session.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as resp:
            data = await resp.json()

            if resp.status != 200:
                raise LLMException(f"OpenRouter error: {data}")

            choice = data["choices"][0]
            content = choice["message"].get("content", "")

            # OpenRouter sometimes returns reasoning
            reasoning = choice["message"].get("reasoning", "")
            if reasoning:
                content = f"[Reasoning: {reasoning}]\n\n{content}"

            return AgentResponse(
                content=content,
                usage=data.get("usage", {}),
                model=data.get("model", self.config.model),
            )

    # ========== STREAMING ==========
    async def _stream_chat(self):
        """Stream chat response (generator)."""
        messages = [msg.to_dict() for msg in self._history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.config.base_url}/chat/completions"
        if self.config.provider == "anthropic":
            url = "https://api.anthropic.com/v1/messages"
            headers["x-api-key"] = self.config.api_key
            headers["anthropic-version"] = "2023-06-01"
            del headers["Authorization"]

        async with self.session.post(url, headers=headers, json=payload) as resp:
            async for line in resp.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if "choices" in chunk:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except:
                        pass

    # ========== TOOLS ==========

    async def _execute_tools(self, tool_calls: List[Dict]) -> List[Any]:
        """Execute tool calls."""
        results = []
        for call in tool_calls:
            tool_name = call.get("function", {}).get("name", "")
            arguments = json.loads(call.get("function", {}).get("arguments", "{}"))

            if self.tool_registry and self.tool_registry.has_tool(tool_name):
                tool = self.tool_registry.get_tool(tool_name)
                try:
                    if asyncio.iscoroutinefunction(tool):
                        result = await tool(**arguments)
                    else:
                        result = tool(**arguments)
                    results.append(result)
                except Exception as e:
                    logger.error("Tool '%s' error: %s", tool_name, e)
                    results.append(f"Error: {e}")
            else:
                results.append(f"Tool '{tool_name}' not found")

        return results

    # ========== MEMORY ==========

    def get_history(self) -> List[Message]:
        """Get chat history."""
        return self._history.copy()

    def clear_history(self):
        """Clear chat history (keep system prompt)."""
        system = self._history[0] if self._history and self._history[0].role == "system" else None
        self._history = [system] if system else []
        logger.info("🧹 History cleared for agent '%s'", self.name)

    # ========== LIFECYCLE ==========

    async def close(self):
        """Close agent and cleanup."""
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("🛑 Agent '%s' closed", self.name)

    def __repr__(self):
        return f"Agent({self.name}, provider={self.config.provider}, model={self.config.model})"
