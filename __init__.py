"""
Agents Claw Mini 🤖⚡
=====================

A lightweight, modular AI Agent Framework for Python.
Inspired by NullClaw (Zig) - bringing the 678KB philosophy to Python.

Features:
- Multi-LLM Support (OpenAI, Anthropic, Google, Mistral, Cohere, Ollama, Groq, DeepSeek, OpenRouter)
- Browser Automation (Selenium, Playwright)
- Web Scraping (BeautifulSoup, Scrapy-like)
- Memory Storage (SQLite, Chroma, Qdrant)
- Messaging Channels (Telegram, Discord, Slack)
- Tool Registry (pluggable tools)
- Security Sandbox
- Async-first design

Author: Agents Claw Mini Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Agents Claw Mini Team"
__license__ = "MIT"

from .core import AgentsClawMini
from .agent import Agent
from .browser import Browser
from .scraper import Scraper
from .channel import ChannelManager
from .memory import Memory
from .tools import ToolRegistry
from .sandbox import Sandbox
from .config import Config
from .utils import Utils
from .exceptions import (
    AgentsClawMiniException,
    AgentException,
    BrowserException,
    ScrapingException,
    ChannelException,
    MemoryException,
    ToolException,
    SandboxException,
    ConfigException,
)

__all__ = [
    "AgentsClawMini",
    "Agent",
    "Browser",
    "Scraper",
    "ChannelManager",
    "Memory",
    "ToolRegistry",
    "Sandbox",
    "Config",
    "Utils",
    "AgentsClawMiniException",
    "AgentException",
    "BrowserException",
    "ScrapingException",
    "ChannelException",
    "MemoryException",
    "ToolException",
    "SandboxException",
    "ConfigException",
]
