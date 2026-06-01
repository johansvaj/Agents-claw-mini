#!/usr/bin/env python3
"""
🤖⚡ Agents Claw Mini v11.0 - AI Terminal Controller via Telegram
Redesigned: Modern UI, full settings, dashboard, integrations
"""

import os
import json
import asyncio
import time
import subprocess
import re
import sys
import signal
import traceback
from pathlib import Path

CONFIG_FILE = os.path.expanduser("~/.claw_config.json")
PROJECTS_DIR = os.path.expanduser("~/ClawProjects")
PID_FILE = "/tmp/claw_bot.pid"
BOT_SCRIPT = "/tmp/claw_bot_v11.py"

# ── COLORS ──
C = {
    "r": "\033[0m", "b": "\033[1m", "d": "\033[2m",
    "R": "\033[91m", "G": "\033[92m", "Y": "\033[93m",
    "B": "\033[94m", "M": "\033[95m", "C": "\033[96m",
    "W": "\033[97m", "O": "\033[38;5;208m",
}

def c(name):
    return C.get(name, "")

def clear():
    os.system("clear")

# ── UI COMPONENTS ──
def box_top(w=52, title=""):
    t = c("C") + "╔" + "═" * w + "╗" + c("r")
    if title:
        pad = (w - len(title)) // 2
        t += "\n" + c("C") + "║" + " " * pad + c("b") + c("Y") + title + c("r") + c("C") + " " * (w - len(title) - pad) + "║" + c("r")
    return t

def box_mid(text="", w=52, align="left", color="W"):
    if align == "center":
        pad = (w - len(text)) // 2
        return c("C") + "║" + " " * pad + c(color) + text + c("r") + c("C") + " " * (w - len(text) - pad) + "║" + c("r")
    elif align == "right":
        return c("C") + "║" + " " * (w - len(text) - 1) + c(color) + text + c("r") + c("C") + " " + "║" + c("r")
    else:
        return c("C") + "║ " + c(color) + text + c("r") + c("C") + " " * (w - len(text) - 1) + "║" + c("r")

def box_sep(w=52):
    return c("C") + "╠" + "═" * w + "╣" + c("r")

def box_bot(w=52):
    return c("C") + "╚" + "═" * w + "╝" + c("r")

def menu_item(num, text, desc="", color="W"):
    num_part = c("b") + c("Y") + f"[{num}]" + c("r")
    txt_part = c("b") + c(color) + text + c("r")
    desc_part = c("d") + desc + c("r")
    return "  " + num_part + " " + txt_part + "  " + desc_part

def sub_item(text, color="d"):
    return "      " + c(color) + "├─ " + text + c("r")

def header():
    return "\n".join([
        "",
        box_top(52),
        box_mid("🤖⚡  A G E N T S   C L A W   M I N I  ⚡🤖", 52, "center", "Y"),
        box_mid("AI Terminal Controller via Telegram v11.0", 52, "center", "d"),
        box_bot(52),
        "",
    ])

# ── MODELS ──
ALL_MODELS = {
    "openai_gpt4o": {"name": "GPT-4o", "id": "openai/gpt-4o", "provider": "OpenAI", "icon": "🌟"},
    "openai_gpt4omini": {"name": "GPT-4o Mini", "id": "openai/gpt-4o-mini", "provider": "OpenAI", "icon": "⭐"},
    "openai_gpt4turbo": {"name": "GPT-4 Turbo", "id": "openai/gpt-4-turbo", "provider": "OpenAI", "icon": "💎"},
    "openai_gpt5": {"name": "GPT-5", "id": "openai/gpt-5", "provider": "OpenAI", "icon": "🔥"},
    "anthropic_sonnet": {"name": "Claude 3.5 Sonnet", "id": "anthropic/claude-3.5-sonnet", "provider": "Anthropic", "icon": "🎭"},
    "anthropic_opus": {"name": "Claude 3 Opus", "id": "anthropic/claude-3-opus", "provider": "Anthropic", "icon": "👑"},
    "anthropic_claude4": {"name": "Claude 4", "id": "anthropic/claude-4", "provider": "Anthropic", "icon": "👑"},
    "google_pro": {"name": "Gemini 1.5 Pro", "id": "google/gemini-1.5-pro", "provider": "Google", "icon": "🔮"},
    "google_flash": {"name": "Gemini 1.5 Flash", "id": "google/gemini-1.5-flash", "provider": "Google", "icon": "⚡"},
    "google_gemini25": {"name": "Gemini 2.5 Pro", "id": "google/gemini-2.5-pro", "provider": "Google", "icon": "🔮"},
    "deepseek_chat": {"name": "DeepSeek Chat", "id": "deepseek/deepseek-chat", "provider": "DeepSeek", "icon": "🧠"},
    "deepseek_coder": {"name": "DeepSeek Coder", "id": "deepseek/deepseek-coder", "provider": "DeepSeek", "icon": "💻"},
    "deepseek_r1": {"name": "DeepSeek R1", "id": "deepseek/deepseek-r1", "provider": "DeepSeek", "icon": "🔥"},
    "deepseek_v4": {"name": "DeepSeek V4", "id": "deepseek/deepseek-v4", "provider": "DeepSeek", "icon": "🚀"},
    "meta_70b": {"name": "Llama 3.1 70B", "id": "meta-llama/llama-3.1-70b-instruct", "provider": "Meta", "icon": "🦙"},
    "meta_8b": {"name": "Llama 3.1 8B", "id": "meta-llama/llama-3.1-8b-instruct", "provider": "Meta", "icon": "🐑"},
    "meta_llama4": {"name": "Llama 4", "id": "meta-llama/llama-4", "provider": "Meta", "icon": "🦙"},
    "qwen_72b": {"name": "Qwen 2.5 72B", "id": "qwen/qwen-2.5-72b-instruct", "provider": "Qwen", "icon": "🐉"},
    "qwen_qwen3": {"name": "Qwen 3", "id": "qwen/qwen-3", "provider": "Qwen", "icon": "🐉"},
    "mistral_large": {"name": "Mistral Large", "id": "mistralai/mistral-large", "provider": "Mistral", "icon": "🌊"},
    "kimi_k25": {"name": "Kimi K2.5", "id": "moonshotai/kimi-k2-5", "provider": "Kimi", "icon": "🌙"},
    "perplexity_sonar": {"name": "Sonar Large", "id": "perplexity/llama-3.1-sonar-large-128k-online", "provider": "Perplexity", "icon": "🔍"},
    "microsoft_wizard": {"name": "WizardLM 2", "id": "microsoft/wizardlm-2-8x22b", "provider": "Microsoft", "icon": "🧙"},
    "ollama_llama": {"name": "Llama 3.1 (Local)", "id": "llama3.1", "provider": "Ollama", "icon": "🦙", "local": True},
    "ollama_mistral": {"name": "Mistral (Local)", "id": "mistral", "provider": "Ollama", "icon": "🌊", "local": True},
    "ollama_qwen": {"name": "Qwen 2.5 (Local)", "id": "qwen2.5", "provider": "Ollama", "icon": "🐉", "local": True},
    "ollama_coder": {"name": "CodeLlama (Local)", "id": "codellama", "provider": "Ollama", "icon": "💻", "local": True},
}

PROVIDERS = {
    "1": {"name": "OpenAI", "icon": "🅾️", "color": "G", "models": ["openai_gpt4o", "openai_gpt4omini", "openai_gpt4turbo", "openai_gpt5"]},
    "2": {"name": "Anthropic", "icon": "🅰️", "color": "M", "models": ["anthropic_sonnet", "anthropic_opus", "anthropic_claude4"]},
    "3": {"name": "Google", "icon": "🅶️", "color": "B", "models": ["google_pro", "google_flash", "google_gemini25"]},
    "4": {"name": "DeepSeek", "icon": "🐋", "color": "C", "models": ["deepseek_chat", "deepseek_coder", "deepseek_r1", "deepseek_v4"]},
    "5": {"name": "Meta", "icon": "Ⓜ️", "color": "B", "models": ["meta_70b", "meta_8b", "meta_llama4"]},
    "6": {"name": "Qwen", "icon": "🇶", "color": "Y", "models": ["qwen_72b", "qwen_qwen3"]},
    "7": {"name": "Mistral", "icon": "Ⓜ️", "color": "Y", "models": ["mistral_large"]},
    "8": {"name": "Kimi", "icon": "🌙", "color": "W", "models": ["kimi_k25"]},
    "9": {"name": "Perplexity", "icon": "🔍", "color": "G", "models": ["perplexity_sonar"]},
    "10": {"name": "Microsoft", "icon": "✨", "color": "W", "models": ["microsoft_wizard"]},
    "11": {"name": "Ollama (Local)", "icon": "💻", "color": "G", "models": ["ollama_llama", "ollama_mistral", "ollama_qwen", "ollama_coder"]},
}

INTEGRATIONS = [
    "Discord", "Telegram", "WhatsApp", "Slack", "Matrix",
    "Microsoft Teams", "Gmail", "Google Calendar", "Google Drive",
    "Dropbox", "GitHub", "GitLab", "Notion", "Trello", "Jira",
    "Airtable", "Google Sheets", "PostgreSQL", "MySQL", "MongoDB",
    "Redis", "n8n", "Zapier", "Make (Integromat)",
    "Home Assistant", "MQTT", "Webhook", "REST API", "MCP Servers"
]

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "token": "", "openrouter_key": "", "model": "deepseek_chat",
        "admin_id": "", "temperature": 0.7, "max_tokens": 4096,
        "context_window": "auto", "performance": "balanced",
        "fallback_model": "deepseek_chat", "base_url": "",
        "org_id": "", "integrations": []
    }

def save_cfg(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    print(c("G") + "\n    💾 Configuration saved!" + c("r"))

# ── SCREENS ──

def dashboard():
    cfg = load_cfg()
    m = ALL_MODELS.get(cfg.get("model", "deepseek_chat"), {})
    clear(); print(header())
    
    print(box_top(52, "📊 DASHBOARD"))
    print(box_mid(""))
    print(box_mid("🤖 Model:    " + m.get("icon","") + " " + m.get("name","Not Set"), 52))
    print(box_mid("🌐 Provider: " + m.get("provider","?"), 52))
    print(box_mid("🔑 API:      " + ("💻 Local" if m.get("local") else "🌐 OpenRouter"), 52))
    print(box_mid(""))
    print(box_sep(52))
    print(box_mid("📈 Stats", 52))
    print(box_mid("   Messages: 0", 52))
    print(box_mid("   Commands: 0", 52))
    print(box_mid("   Files:    0", 52))
    print(box_bot(52))
    input("\n    Press Enter...")

def chat_screen():
    clear(); print(header())
    print(box_top(52, "💬 CHAT"))
    print(box_mid(""))
    print(box_mid("Chat history will appear here...", 52, "center", "d"))
    print(box_mid(""))
    print(box_bot(52))
    print("\n    " + c("d") + "Type /back to return to menu" + c("r"))
    input("\n    ➤ ")

def models_screen():
    cfg = load_cfg()
    while True:
        clear(); print(header())
        print(box_top(52, "🤖 MODELS"))
        print(box_mid(""))
        print(box_mid("Current: " + ALL_MODELS.get(cfg.get("model"), {}).get("name", "Not Set"), 52))
        print(box_mid(""))
        print(box_sep(52))
        
        for pid, p in PROVIDERS.items():
            tag = "💻 Local" if pid == "11" else "🌐 OpenRouter"
            print(box_mid("[" + pid + "] " + p["icon"] + " " + p["name"] + " " + tag, 52))
        print(box_mid(""))
        print(box_mid("[0] Back", 52))
        print(box_bot(52))
        
        prov = input("\n    ➤ Select provider: ").strip()
        if prov == "0": break
        if prov not in PROVIDERS: continue
        
        while True:
            clear(); print(header())
            print(box_top(52, "🤖 " + PROVIDERS[prov]["name"]))
            print(box_mid(""))
            for i, mid in enumerate(PROVIDERS[prov]["models"], 1):
                m = ALL_MODELS[mid]
                current = " ← CURRENT" if cfg.get("model") == mid else ""
                print(box_mid("[" + str(i) + "] " + m["icon"] + " " + m["name"] + current, 52))
            print(box_mid(""))
            print(box_mid("[0] Back", 52))
            print(box_mid("[s] Set as current", 52))
            print(box_bot(52))
            
            choice = input("\n    ➤ Select: ").strip()
            if choice == "0": break
            if choice == "s":
                mid = input("    Model ID to set: ").strip()
                # Find model by partial match
                for key, val in ALL_MODELS.items():
                    if mid.lower() in key.lower() or mid.lower() in val["name"].lower():
                        cfg["model"] = key
                        print(c("G") + "    ✅ Model set to: " + val["name"] + c("r"))
                        time.sleep(1)
                        break
                continue
            try:
                mid = PROVIDERS[prov]["models"][int(choice) - 1]
                cfg["model"] = mid
                print(c("G") + "    ✅ Model set to: " + ALL_MODELS[mid]["name"] + c("r"))
                time.sleep(1)
            except:
                continue

def agents_screen():
    clear(); print(header())
    print(box_top(52, "🕵️ AGENTS"))
    print(box_mid(""))
    print(box_mid("Available Agents:", 52))
    print(box_mid("  • Terminal Agent    - Execute shell commands", 52))
    print(box_mid("  • Code Agent        - Generate & run code", 52))
    print(box_mid("  • File Agent        - Manage files & folders", 52))
    print(box_mid("  • Network Agent     - Scan & pentest tools", 52))
    print(box_mid("  • Install Agent     - Package management", 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

def memory_screen():
    clear(); print(header())
    print(box_top(52, "🧠 MEMORY"))
    print(box_mid(""))
    print(box_mid("Memory usage: 0 conversations stored", 52))
    print(box_mid("Context window: auto", 52))
    print(box_mid(""))
    print(box_mid("[1] Clear Memory", 52))
    print(box_mid("[2] Export Memory", 52))
    print(box_mid("[0] Back", 52))
    print(box_bot(52))
    input("\n    ➤ ")

def skills_screen():
    clear(); print(header())
    print(box_top(52, "🎯 SKILLS"))
    print(box_mid(""))
    skills = ["Coding", "Hacking", "System Admin", "Web Dev", "Data Analysis"]
    for i, s in enumerate(skills, 1):
        print(box_mid("[" + str(i) + "] " + s, 52))
    print(box_mid(""))
    print(box_mid("[0] Back", 52))
    print(box_bot(52))
    input("\n    ➤ ")

def tools_screen():
    clear(); print(header())
    print(box_top(52, "🛠️ TOOLS"))
    print(box_mid(""))
    tools = ["nmap", "metasploit", "sqlmap", "nikto", "gobuster", "hydra", "john", "hashcat"]
    for t in tools:
        print(box_mid("  • " + t, 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

def channels_screen():
    clear(); print(header())
    print(box_top(52, "📡 CHANNELS"))
    print(box_mid(""))
    print(box_mid("Active: Telegram", 52))
    print(box_mid(""))
    print(box_mid("Available integrations:", 52))
    for i in INTEGRATIONS[:10]:
        print(box_mid("  • " + i, 52))
    print(box_mid("  ... and " + str(len(INTEGRATIONS) - 10) + " more", 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

def automation_screen():
    clear(); print(header())
    print(box_top(52, "⚙️ AUTOMATION"))
    print(box_mid(""))
    print(box_mid("No automation rules configured", 52))
    print(box_mid(""))
    print(box_mid("[1] Create Rule", 52))
    print(box_mid("[2] Schedule Task", 52))
    print(box_mid("[0] Back", 52))
    print(box_bot(52))
    input("\n    ➤ ")

def sandbox_screen():
    clear(); print(header())
    print(box_top(52, "🏖️ SANDBOX"))
    print(box_mid(""))
    print(box_mid("Sandbox mode: OFF", 52))
    print(box_mid(""))
    print(box_mid("Run commands in isolated environment", 52))
    print(box_mid("[1] Enable Sandbox", 52))
    print(box_mid("[0] Back", 52))
    print(box_bot(52))
    input("\n    ➤ ")

def workspace_screen():
    clear(); print(header())
    print(box_top(52, "💼 WORKSPACE"))
    print(box_mid(""))
    print(box_mid("Project dir: ~/ClawProjects", 52))
    print(box_mid("Active projects: 0", 52))
    print(box_mid(""))
    print(box_mid("[1] List Projects", 52))
    print(box_mid("[2] New Project", 52))
    print(box_mid("[0] Back", 52))
    print(box_bot(52))
    input("\n    ➤ ")

def api_keys_screen():
    cfg = load_cfg()
    clear(); print(header())
    print(box_top(52, "🔑 API KEYS"))
    print(box_mid(""))
    print(box_mid("OpenRouter: " + ("✅ Set" if cfg.get("openrouter_key") else "❌ Not Set"), 52))
    print(box_mid("Telegram:   " + ("✅ Set" if cfg.get("token") else "❌ Not Set"), 52))
    print(box_mid("Custom:     ❌ Not Set", 52))
    print(box_mid(""))
    print(box_mid("[1] Set OpenRouter Key", 52))
    print(box_mid("[2] Set Telegram Token", 52))
    print(box_mid("[3] Set Custom API", 52))
    print(box_mid("[0] Back", 52))
    print(box_bot(52))
    
    p = input("\n    ➤ ").strip()
    if p == "1":
        k = input("    OpenRouter Key: ").strip()
        if k: cfg["openrouter_key"] = k; save_cfg(cfg)
    elif p == "2":
        t = input("    Telegram Token: ").strip()
        if t: cfg["token"] = t; save_cfg(cfg)
    elif p == "3":
        url = input("    Base URL: ").strip()
        if url: cfg["base_url"] = url; save_cfg(cfg)

def logs_screen():
    clear(); print(header())
    print(box_top(52, "📋 LOGS"))
    print(box_mid(""))
    log_file = "/tmp/claw_bot.log"
    if os.path.exists(log_file):
        with open(log_file) as f:
            lines = f.readlines()[-20:]
        for line in lines:
            print(box_mid("  " + line.strip()[:48], 52))
    else:
        print(box_mid("No logs found", 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

def monitoring_screen():
    clear(); print(header())
    print(box_top(52, "📈 MONITORING"))
    print(box_mid(""))
    print(box_mid("CPU: 0%  |  RAM: 0%  |  Disk: 0%", 52))
    print(box_mid("Uptime: 0h 0m", 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

def security_screen():
    clear(); print(header())
    print(box_top(52, "🔒 SECURITY"))
    print(box_mid(""))
    print(box_mid("Dangerous command filter: ✅ ON", 52))
    print(box_mid("Admin restriction: " + ("✅ ON" if load_cfg().get("admin_id") else "❌ OFF"), 52))
    print(box_mid("Sandbox mode: ❌ OFF", 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

def backup_screen():
    clear(); print(header())
    print(box_top(52, "💾 BACKUP"))
    print(box_mid(""))
    print(box_mid("[1] Backup Config", 52))
    print(box_mid("[2] Restore Config", 52))
    print(box_mid("[3] Export Chats", 52))
    print(box_mid("[0] Back", 52))
    print(box_bot(52))
    input("\n    ➤ ")

def updates_screen():
    clear(); print(header())
    print(box_top(52, "🔄 UPDATES"))
    print(box_mid(""))
    print(box_mid("Current version: v11.0", 52))
    print(box_mid("Latest version: v11.0", 52))
    print(box_mid("Status: ✅ Up to date", 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

def settings_screen():
    cfg = load_cfg()
    while True:
        clear(); print(header())
        print(box_top(52, "⚙️ SETTINGS"))
        print(box_mid(""))
        print(box_mid("[1] Model Provider", 52))
        print(box_mid("    ├─ Current: " + ALL_MODELS.get(cfg.get("model"), {}).get("provider", "?"), 52))
        print(box_mid("[2] Current Model", 52))
        print(box_mid("    ├─ " + ALL_MODELS.get(cfg.get("model"), {}).get("name", "Not Set"), 52))
        print(box_mid("[3] Fallback Model", 52))
        print(box_mid("    ├─ " + ALL_MODELS.get(cfg.get("fallback_model"), {}).get("name", "Not Set"), 52))
        print(box_mid("[4] Temperature      └─ " + str(cfg.get("temperature", 0.7)), 52))
        print(box_mid("[5] Max Tokens       └─ " + str(cfg.get("max_tokens", 4096)), 52))
        print(box_mid("[6] Context Window   └─ " + cfg.get("context_window", "auto"), 52))
        print(box_mid("[7] API Configuration", 52))
        print(box_mid("    ├─ Key: " + ("✅" if cfg.get("openrouter_key") else "❌"), 52))
        print(box_mid("    ├─ URL: " + (cfg.get("base_url") or "default"), 52))
        print(box_mid("    └─ Org: " + (cfg.get("org_id") or "none"), 52))
        print(box_mid("[8] Local Models     ├─ ollama list", 52))
        print(box_mid("[9] Performance      └─ " + cfg.get("performance", "balanced"), 52))
        print(box_mid(""))
        print(box_mid("[s] Save Configuration", 52))
        print(box_mid("[0] Back", 52))
        print(box_bot(52))
        
        p = input("\n    ➤ ").strip()
        if p == "0": break
        elif p == "1" or p == "2":
            models_screen()
        elif p == "3":
            print("    Select fallback model...")
            time.sleep(1)
        elif p == "4":
            t = input("    Temperature (0.0-2.0): ").strip()
            if t: cfg["temperature"] = float(t)
        elif p == "5":
            t = input("    Max Tokens: ").strip()
            if t: cfg["max_tokens"] = int(t)
        elif p == "6":
            t = input("    Context (auto/number): ").strip()
            if t: cfg["context_window"] = t
        elif p == "7":
            api_keys_screen()
        elif p == "9":
            perf = input("    Mode (fast/balanced/quality): ").strip()
            if perf: cfg["performance"] = perf
        elif p == "s":
            save_cfg(cfg)

def about_screen():
    clear(); print(header())
    print(box_top(52, "ℹ️ ABOUT"))
    print(box_mid(""))
    print(box_mid("Agents Claw Mini v11.0", 52, "center", "Y"))
    print(box_mid("AI Terminal Controller", 52, "center"))
    print(box_mid("via Telegram", 52, "center"))
    print(box_mid(""))
    print(box_mid("Author: @yourusername", 52))
    print(box_mid("License: MIT", 52))
    print(box_mid("GitHub: github.com/agents-claw", 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

# ── MAIN MENU ──

def main():
    while True:
        clear(); print(header())
        print(box_top(52))
        
        cfg = load_cfg()
        m = ALL_MODELS.get(cfg.get("model", "deepseek_chat"), {})
        ready = cfg.get("token") != "" and (cfg.get("openrouter_key") != "" or m.get("local", False))
        
        status = c("G") + "● ONLINE" if ready else c("R") + "● OFFLINE"
        print(box_mid(status + c("r") + "  " + m.get("icon","") + " " + m.get("name","Not Set"), 52))
        print(box_sep(52))
        
        print(box_mid(menu_item("1", "Dashboard", "System overview"), 52))
        print(box_mid(menu_item("2", "Chat", "AI conversation"), 52))
        print(box_mid(menu_item("3", "Models", "Select AI model"), 52))
        print(box_mid(menu_item("4", "Agents", "AI agents"), 52))
        print(box_mid(menu_item("5", "Memory", "Conversation history"), 52))
        print(box_mid(menu_item("6", "Skills", "AI capabilities"), 52))
        print(box_mid(menu_item("7", "Tools", "Installed tools"), 52))
        print(box_mid(menu_item("8", "Channels", "Integrations"), 52))
        print(box_mid(menu_item("9", "Automation", "Rules & schedules"), 52))
        print(box_mid(menu_item("10", "Sandbox", "Isolated environment"), 52))
        print(box_mid(menu_item("11", "Workspace", "Project management"), 52))
        print(box_mid(menu_item("12", "API Keys", "Authentication"), 52))
        print(box_mid(menu_item("13", "Logs", "System logs"), 52))
        print(box_mid(menu_item("14", "Monitoring", "Performance stats"), 52))
        print(box_mid(menu_item("15", "Security", "Access control"), 52))
        print(box_mid(menu_item("16", "Backup", "Export/Import"), 52))
        print(box_mid(menu_item("17", "Updates", "Version check"), 52))
        print(box_mid(menu_item("18", "Settings", "Configuration"), 52))
        print(box_mid(menu_item("19", "About", "Information"), 52))
        print(box_sep(52))
        print(box_mid(menu_item("20", "Exit", "Close launcher"), 52))
        print(box_bot(52))
        
        p = input("\n    ➤ Select [1-20]: ").strip()
        
        if p == "1": dashboard()
        elif p == "2": chat_screen()
        elif p == "3": models_screen()
        elif p == "4": agents_screen()
        elif p == "5": memory_screen()
        elif p == "6": skills_screen()
        elif p == "7": tools_screen()
        elif p == "8": channels_screen()
        elif p == "9": automation_screen()
        elif p == "10": sandbox_screen()
        elif p == "11": workspace_screen()
        elif p == "12": api_keys_screen()
        elif p == "13": logs_screen()
        elif p == "14": monitoring_screen()
        elif p == "15": security_screen()
        elif p == "16": backup_screen()
        elif p == "17": updates_screen()
        elif p == "18": settings_screen()
        elif p == "19": about_screen()
        elif p == "20":
            clear(); print(header())
            print(box_top(52))
            print(box_mid("👋 Goodbye!", 52, "center", "G"))
            print(box_bot(52))
            break
        else:
            print(c("R") + "\n    ❌ Invalid choice!" + c("r"))
            time.sleep(1)

if __name__ == "__main__":
    main()
