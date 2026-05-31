"""Configuration manager for Agents Claw Mini."""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from .exceptions import ConfigException

# ===== OPENROUTER MODELS =====
OPENROUTER_MODELS = {
    # OpenAI
    "openai/gpt-4o": "OpenAI GPT-4o",
    "openai/gpt-4o-mini": "OpenAI GPT-4o Mini",
    "openai/gpt-4-turbo": "OpenAI GPT-4 Turbo",
    "openai/gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo",
    # Anthropic
    "anthropic/claude-3.5-sonnet": "Anthropic Claude 3.5 Sonnet",
    "anthropic/claude-3-opus": "Anthropic Claude 3 Opus",
    "anthropic/claude-3-haiku": "Anthropic Claude 3 Haiku",
    # Google
    "google/gemini-1.5-pro": "Google Gemini 1.5 Pro",
    "google/gemini-1.5-flash": "Google Gemini 1.5 Flash",
    "google/gemini-pro": "Google Gemini Pro",
    # Meta
    "meta-llama/llama-3.1-70b-instruct": "Meta Llama 3.1 70B",
    "meta-llama/llama-3.1-8b-instruct": "Meta Llama 3.1 8B",
    "meta-llama/llama-3-70b-instruct": "Meta Llama 3 70B",
    # Mistral
    "mistralai/mistral-large": "Mistral Large",
    "mistralai/mistral-medium": "Mistral Medium",
    "mistralai/mistral-small": "Mistral Small",
    "mistralai/mixtral-8x22b-instruct": "Mixtral 8x22B",
    # Nous
    "nousresearch/hermes-3-llama-3.1-70b": "Nous Hermes 3 70B",
    # Qwen
    "qwen/qwen-2.5-72b-instruct": "Qwen 2.5 72B",
    "qwen/qwen-2-72b-instruct": "Qwen 2 72B",
    # DeepSeek
    "deepseek/deepseek-chat": "DeepSeek Chat",
    "deepseek/deepseek-coder": "DeepSeek Coder",
    # Perplexity
    "perplexity/llama-3.1-sonar-large-128k-online": "Perplexity Sonar Large",
    # Microsoft
    "microsoft/wizardlm-2-8x22b": "Microsoft WizardLM 2 8x22B",
    # Others
    "gryphe/mythomax-l2-13b": "MythoMax L2 13B",
    "huggingfaceh4/zephyr-7b-beta": "Zephyr 7B",
    "openchat/openchat-7b": "OpenChat 7B",
}

# ===== PROVIDER CONFIGURATIONS =====
PROVIDER_CONFIGS = {
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
    },
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com",
        "default_model": "claude-3-5-sonnet-20241022",
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
    },
    "google": {
        "env_key": "GOOGLE_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com",
        "default_model": "gemini-1.5-pro",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
    },
    "mistral": {
        "env_key": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
        "default_model": "mistral-large-latest",
        "models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "mixtral-8x22b-2404"],
    },
    "cohere": {
        "env_key": "COHERE_API_KEY",
        "base_url": "https://api.cohere.com",
        "default_model": "command-r-plus",
        "models": ["command-r-plus", "command-r", "command"],
    },
    "groq": {
        "env_key": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-70b-versatile",
        "models": [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
        ],
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-coder"],
    },
    "ollama": {
        "env_key": None,
        "base_url": "http://localhost:11434",
        "default_model": "llama3.1",
        "models": ["llama3.1", "llama3", "phi3", "mistral", "gemma2", "qwen2.5"],
    },
    "openrouter": {
        "env_key": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "openai/gpt-4o",
        "models": list(OPENROUTER_MODELS.keys()),
    },
}

@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    def __post_init__(self):
        provider_info = PROVIDER_CONFIGS.get(self.provider)
        if not provider_info:
            raise ConfigException(f"Provider '{self.provider}' tidak didukung. Pilih dari: {list(PROVIDER_CONFIGS.keys())}")

        # Set default model jika tidak ditentukan
        if not self.model or self.model == "default":
            self.model = provider_info["default_model"]

        # Set base_url jika tidak ditentukan
        if not self.base_url:
            self.base_url = provider_info["base_url"]

        # Get API key dari environment jika tidak ditentukan
        if not self.api_key and provider_info["env_key"]:
            self.api_key = os.getenv(provider_info["env_key"])
            if not self.api_key:
                raise ConfigException(
                    f"API key untuk {self.provider} tidak ditemukan. "
                    f"Set environment variable {provider_info['env_key']} atau pass api_key langsung."
                )

    @classmethod
    def list_providers(cls) -> List[str]:
        """List semua provider yang didukung."""
        return list(PROVIDER_CONFIGS.keys())

    @classmethod
    def list_models(cls, provider: str) -> List[str]:
        """List semua model untuk provider tertentu."""
        provider_info = PROVIDER_CONFIGS.get(provider)
        if provider_info:
            return provider_info["models"]
        return []

    @classmethod
    def list_openrouter_models(cls) -> Dict[str, str]:
        """List semua model OpenRouter dengan nama lengkap."""
        return OPENROUTER_MODELS.copy()

@dataclass
class BrowserConfig:
    """Configuration for browser automation."""
    headless: bool = True
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    timeout: int = 30
    window_width: int = 1920
    window_height: int = 1080
    disable_images: bool = True
    stealth_mode: bool = True
    driver: str = "selenium"  # selenium, playwright

@dataclass
class MemoryConfig:
    """Configuration for memory storage."""
    backend: str = "sqlite"
    db_path: str = "./agents_claw_memory.db"
    vector_dimension: int = 1536
    max_history: int = 1000

@dataclass
class ChannelConfig:
    """Configuration for messaging channels."""
    telegram_token: Optional[str] = None
    discord_token: Optional[str] = None
    slack_token: Optional[str] = None
    whatsapp_session: Optional[str] = None

@dataclass
class SandboxConfig:
    """Configuration for security sandbox."""
    enabled: bool = True
    max_execution_time: int = 30
    allowed_modules: list = field(default_factory=list)
    blocked_modules: list = field(default_factory=lambda: ["os", "subprocess", "sys"])
    max_memory_mb: int = 512

class Config:
    """Main configuration class for Agents Claw Mini."""

    def __init__(self, config_path: Optional[str] = None):
        self.llm = LLMConfig()
        self.browser = BrowserConfig()
        self.memory = MemoryConfig()
        self.channel = ChannelConfig()
        self.sandbox = SandboxConfig()

        if config_path:
            self.load(config_path)

    def load(self, path: str) -> None:
        """Load configuration from file (JSON or YAML)."""
        path = Path(path)
        if not path.exists():
            raise ConfigException(f"File konfigurasi tidak ditemukan: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)

            if "llm" in data:
                self.llm = LLMConfig(**data["llm"])
            if "browser" in data:
                self.browser = BrowserConfig(**data["browser"])
            if "memory" in data:
                self.memory = MemoryConfig(**data["memory"])
            if "channel" in data:
                self.channel = ChannelConfig(**data["channel"])
            if "sandbox" in data:
                self.sandbox = SandboxConfig(**data["sandbox"])

        except Exception as e:
            raise ConfigException(f"Gagal memuat konfigurasi: {e}")

    def save(self, path: str) -> None:
        """Save configuration to file."""
        path = Path(path)
        data = {
            "llm": asdict(self.llm),
            "browser": asdict(self.browser),
            "memory": asdict(self.memory),
            "channel": asdict(self.channel),
            "sandbox": asdict(self.sandbox),
        }

        with open(path, "w", encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                yaml.dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "llm": asdict(self.llm),
            "browser": asdict(self.browser),
            "memory": asdict(self.memory),
            "channel": asdict(self.channel),
            "sandbox": asdict(self.sandbox),
        }
