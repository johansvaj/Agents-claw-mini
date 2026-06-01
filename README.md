# Buat file README.md yang baru dan lengkap
readme_content = """<!-- Banner -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:00C9FF,100:92FE9D&height=200&section=header&text=🤖%20AGENTS%20CLAW%20MINI&fontSize=50&fontColor=ffffff&animation=fadeIn&fontAlignY=35" />
</p>

<!-- Badges -->
<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/></a>
  <a href="https://core.telegram.org/bots/api"><img src="https://img.shields.io/badge/Telegram%20Bot-API%2026B0DA?style=for-the-badge&logo=telegram&logoColor=white"/></a>
  <a href="https://openrouter.ai"><img src="https://img.shields.io/badge/OpenRouter-AI%20Gateway-FF6B6B?style=for-the-badge&logo=openai&logoColor=white"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Termux%20%7C%20WSL-4ECDC4?style=for-the-badge&logo=linux&logoColor=white"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge"/></a>
  <br>
  <a href="#"><img src="https://img.shields.io/badge/Status-Stable%20v12.0-success?style=flat-square"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Tests-Passing-brightgreen?style=flat-square"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Stars-⭐⭐⭐⭐⭐-FFD700?style=flat-square"/></a>
</p>

<!-- Typing Animation -->
<p align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=00C9FF&center=true&vCenter=true&width=600&lines=AI+Terminal+Controller+via+Telegram;Multi-Platform+%7C+Multi-Model+%7C+Multi-Language;Your+Pocket+AI+Assistant+🚀" alt="Typing SVG" />
  </a>
</p>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🎬 Demo](#-demo)
- [📦 Installation](#-installation)
  - [Linux / Debian / Ubuntu / Kali](#linux--debian--ubuntu--kali)
  - [Termux (Android)](#termux-android)
  - [macOS](#macos)
  - [Windows (WSL)](#windows-wsl)
  - [Docker](#docker)
- [⚙️ Configuration](#️-configuration)
- [🚀 Usage](#-usage)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [📁 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 AI Engine (OpenRouter)
- **20+ AI Models** — OpenAI, Anthropic, Google, DeepSeek, Meta, Qwen, Mistral, Kimi, Perplexity, Microsoft, Ollama (Local)
- **Smart Intent Detection** — Auto-detect coding, file ops, system commands
- **Context-Aware** — OS detection for platform-specific responses
- **Conversation Memory** — Persistent chat history per user
- **Powered by OpenRouter** — Unified API for all major AI providers

</td>
<td width="50%">

### 📁 File Manager
- Create / Read / Write / Delete files & folders
- Natural language commands: *"buat file test.py"*
- Directory navigation with `cd`
- AI-powered file operations
- Upload & download files via Telegram

</td>
</tr>
<tr>
<td width="50%">

### 💻 Terminal Integration
- OS Auto-Detection (Linux, macOS, Termux, WSL, Docker)
- Package manager detection (apt, pacman, brew, pkg, etc.)
- System info dashboard
- Shell-aware command suggestions
- Real-time command execution output

</td>
<td width="50%">

### 🔒 Security
- Admin ID restriction
- Dangerous command filtering
- Sandbox mode (planned)
- Access control per Telegram user
- Command whitelist/blacklist

</td>
</tr>
</table>

### 🌐 Multi-Platform Support

| Platform | Status | Install Method |
|----------|--------|----------------|
| 🐧 Linux (Debian/Ubuntu/Kali) | ✅ Fully Supported | `apt` + `pip` |
| 📱 Termux (Android) | ✅ Fully Supported | `pkg` + `pip` |
| 🍎 macOS | ✅ Supported | `brew` + `pip` |
| 🪟 Windows WSL | ✅ Supported | `apt` + `pip` |
| 🐳 Docker | 🔄 Planned | `docker-compose` |

---

## 🎬 Demo

<p align="center">
  <img src="https://raw.githubusercontent.com/AgentsClaw/AgentsClaw-Mini/main/assets/demo.gif" alt="Demo GIF" width="600"/>
</p>

> **Note:** Demo shows real-time terminal control via Telegram with AI-powered responses.

---

## 📦 Installation

### Linux / Debian / Ubuntu / Kali

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Clone repository
git clone https://github.com/AgentsClaw/AgentsClaw-Mini.git
cd AgentsClaw-Mini

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure (see Configuration section)
cp config.example.json config.json
nano config.json

# Run
python3 main.py
```

### Termux (Android)

```bash
# Update packages
pkg update && pkg upgrade -y

# Install dependencies
pkg install python git -y

# Clone repository
git clone https://github.com/AgentsClaw/AgentsClaw-Mini.git
cd AgentsClaw-Mini

# Install requirements
pip install -r requirements.txt

# Configure
cp config.example.json config.json
nano config.json

# Run
python main.py
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 git

# Clone repository
git clone https://github.com/AgentsClaw/AgentsClaw-Mini.git
cd AgentsClaw-Mini

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure
cp config.example.json config.json
nano config.json

# Run
python3 main.py
```

### Windows (WSL)

```bash
# Open WSL terminal
wsl

# Follow Linux installation steps above
sudo apt update && sudo apt install python3 python3-pip git -y
# ... (same as Linux)
```

### Docker

```bash
# Coming soon
docker-compose up -d
```

---

## ⚙️ Configuration

### 1. Get OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai)
2. Sign up / Log in
3. Go to **Keys** → **Create Key**
4. Copy your API key

### 2. Get Telegram Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow instructions to create bot
4. Copy the **Bot Token**

### 3. Get Your Telegram User ID

1. Message [@userinfobot](https://t.me/userinfobot)
2. Copy your **User ID**

### 4. Edit `config.json`

```json
{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "admin_id": 123456789,
    "allowed_users": [123456789]
  },
  "openrouter": {
    "api_key": "YOUR_OPENROUTER_API_KEY_HERE",
    "model": "anthropic/claude-3.5-sonnet",
    "fallback_models": [
      "openai/gpt-4o",
      "google/gemini-pro-1.5",
      "deepseek/deepseek-chat"
    ],
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "system": {
    "auto_detect_os": true,
    "dangerous_commands_filter": true,
    "conversation_memory": true,
    "max_history": 50,
    "language": "auto"
  },
  "features": {
    "file_manager": true,
    "terminal_integration": true,
    "system_info": true,
    "upload_download": true
  }
}
```

### Available OpenRouter Models

| Model | ID | Best For |
|-------|-----|----------|
| Claude 3.5 Sonnet | `anthropic/claude-3.5-sonnet` | Coding, reasoning |
| GPT-4o | `openai/gpt-4o` | General purpose |
| Gemini Pro 1.5 | `google/gemini-pro-1.5` | Long context |
| DeepSeek V3 | `deepseek/deepseek-chat` | Cost-effective |
| Llama 3.1 70B | `meta-llama/llama-3.1-70b-instruct` | Open source |
| Qwen 2.5 72B | `qwen/qwen-2.5-72b-instruct` | Multilingual |
| Mistral Large | `mistralai/mistral-large` | European languages |
| Kimi K2 | `moonshotai/kimi-k2` | Chinese context |
| Perplexity Sonar | `perplexity/sonar` | Web search |
| Ollama (Local) | `ollama/llama3.1` | Privacy-focused |

> **Full list:** [OpenRouter Models](https://openrouter.ai/models)

---

## 🚀 Usage

### Start the Bot

```bash
# With virtual environment
source venv/bin/activate
python3 main.py

# Or using systemd (Linux)
sudo systemctl enable agentsclaw
sudo systemctl start agentsclaw
```

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot & show menu |
| `/help` | Show all commands |
| `/ai <prompt>` | Ask AI anything |
| `/cmd <command>` | Execute terminal command |
| `/file` | File manager menu |
| `/sys` | System info dashboard |
| `/model` | Change AI model |
| `/history` | View conversation history |
| `/clear` | Clear chat history |
| `/status` | Bot status & uptime |

### Natural Language Examples

```
💬 "buat file hello.py dengan isi print('Hello World')"
💬 "install package numpy"
💬 "tampilkan info sistem"
💬 "cd /home && ls -la"
💬 "buat folder project baru"
```

### AI-Powered Features

```
🤖 "buat script python untuk download gambar dari URL"
🤖 "debug error ini: [paste error]"
🤖 "convert json ke csv"
🤖 "buat dockerfile untuk flask app"
🤖 "optimize query SQL ini"
```

---

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Invalid bot token` | Check token with @BotFather |
| `OpenRouter 401` | Verify API key at openrouter.ai |
| `Permission denied` | Run with `sudo` or check file permissions |
| `Command not found` | Ensure binary is in PATH |
| `Telegram timeout` | Check internet connection |

### Logs & Debug

```bash
# View logs
tail -f logs/agentsclaw.log

# Debug mode
python3 main.py --debug

# Verbose output
python3 main.py -v
```

### Support

- 📧 Email: support@agentsclaw.dev
- 💬 Telegram: [@AgentsClawSupport](https://t.me/AgentsClawSupport)
- 🐛 Issues: [GitHub Issues](https://github.com/AgentsClaw/AgentsClaw-Mini/issues)

---

## 📁 Project Structure

```
AgentsClaw-Mini/
├── 📄 main.py                 # Entry point
├── 📁 bot/
│   ├── __init__.py
│   ├── telegram_bot.py        # Telegram bot handler
│   ├── ai_engine.py           # OpenRouter AI integration
│   ├── file_manager.py        # File operations
│   ├── terminal.py            # Terminal command execution
│   ├── security.py            # Access control & filtering
│   ├── system_info.py         # OS detection & info
│   └── memory.py              # Conversation history
├── 📁 config/
│   ├── config.json            # User configuration
│   └── config.example.json    # Example config
├── 📁 logs/
│   └── agentsclaw.log         # Runtime logs
├── 📁 assets/
│   └── demo.gif               # Demo media
├── 📄 requirements.txt        # Python dependencies
├── 📄 Dockerfile              # Docker config
├── 📄 docker-compose.yml      # Docker Compose
├── 📄 LICENSE                 # MIT License
└── 📄 README.md               # This file
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Clone** your fork
3. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
4. **Commit** your changes (`git commit -m 'Add amazing feature'`)
5. **Push** to the branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black bot/
flake8 bot/
```

### Contributors

<a href="https://github.com/AgentsClaw/AgentsClaw-Mini/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AgentsClaw/AgentsClaw-Mini" />
</a>

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Agents Claw Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE



```


---

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai) — Unified AI API Gateway
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — Telegram Bot Framework
- [Termux](https://termux.dev) — Android Terminal Emulator
- [Contributors](https://github.com/AgentsClaw/AgentsClaw-Mini/graphs/contributors) — All amazing contributors

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:92FE9D,100:00C9FF&height=100&section=footer" />
</p>

<p align="center">
  Made with ❤️ by <strong>Agents Claw Team</strong>
  <br>
  <a href="https://t.me/AgentsClaw">Telegram</a> •
  <a href="https://github.com/AgentsClaw">GitHub</a> •
  <a href="https://agentsclaw.dev">Website</a>
</p>
"""

# Tulis ke file baru
output_path = "/mnt/agents/output/AGENTS_CLAW_MINI_README.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(readme_content)

print("✅ File berhasil dibuat!")
print(f"📁 Nama file: AGENTS_CLAW_MINI_README.md")
print(f"📂 Lokasi: {output_path}")
print(f"📊 Ukuran: {len(readme_content)} karakter")
