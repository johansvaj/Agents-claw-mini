�

�
￼ 

�

�
￼ ￼ ￼ ￼ ￼ 
￼ ￼ ￼ 

�

�
￼ 

📋 Table of Contents
✨ Features
🎬 Demo
📦 Installation
Linux / Debian / Ubuntu / Kali
Termux (Android)
macOS
Windows (WSL)
Docker
⚙️ Configuration
🚀 Usage
🛠️ Troubleshooting
📁 Project Structure
🤝 Contributing
📜 License
✨ Features
�

🤖 AI Engine (OpenRouter)
20+ AI Models — OpenAI, Anthropic, Google, DeepSeek, Meta, Qwen, Mistral, Kimi, Perplexity, Microsoft, Ollama (Local)
Smart Intent Detection — Auto-detect coding, file ops, system commands
Context-Aware — OS detection for platform-specific responses
Conversation Memory — Persistent chat history per user
Powered by OpenRouter — Unified API for all major AI providers
�

📁 File Manager
Create / Read / Write / Delete files & folders
Natural language commands: "buat file test.py"
Directory navigation with cd
AI-powered file operations
Upload & download files via Telegram
�

💻 Terminal Integration
OS Auto-Detection (Linux, macOS, Termux, WSL, Docker)
Package manager detection (apt, pacman, brew, pkg, etc.)
System info dashboard
Shell-aware command suggestions
Real-time command execution output
�

🔒 Security
Admin ID restriction
Dangerous command filtering
Sandbox mode (planned)
Access control per Telegram user
Command whitelist/blacklist
�

🌐 Multi-Platform Support
Platform
Status
Install Method
🐧 Linux (Debian/Ubuntu/Kali)
✅ Fully Supported
apt + pip
📱 Termux (Android)
✅ Fully Supported
pkg + pip
🍎 macOS
✅ Supported
brew + pip
🪟 Windows WSL
✅ Supported
apt + pip
🐳 Docker
🔄 Planned
docker-compose
🎬 Demo
�
￼ 

Note: Demo shows real-time terminal control via Telegram with AI-powered responses.
📦 Installation
Linux / Debian / Ubuntu / Kali
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
Termux (Android)
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
macOS
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
Windows (WSL)
# Open WSL terminal
wsl

# Follow Linux installation steps above
sudo apt update && sudo apt install python3 python3-pip git -y
# ... (same as Linux)
Docker
# Coming soon
docker-compose up -d
⚙️ Configuration
1. Get OpenRouter API Key
Visit OpenRouter
Sign up / Log in
Go to Keys → Create Key
Copy your API key
2. Get Telegram Bot Token
Message @BotFather on Telegram
Send /newbot
Follow instructions to create bot
Copy the Bot Token
3. Get Your Telegram User ID
Message @userinfobot
Copy your User ID
4. Edit config.json
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
Available OpenRouter Models
Model
ID
Best For
Claude 3.5 Sonnet
anthropic/claude-3.5-sonnet
Coding, reasoning
GPT-4o
openai/gpt-4o
General purpose
Gemini Pro 1.5
google/gemini-pro-1.5
Long context
DeepSeek V3
deepseek/deepseek-chat
Cost-effective
Llama 3.1 70B
meta-llama/llama-3.1-70b-instruct
Open source
Qwen 2.5 72B
qwen/qwen-2.5-72b-instruct
Multilingual
Mistral Large
mistralai/mistral-large
European languages
Kimi K2
moonshotai/kimi-k2
Chinese context
Perplexity Sonar
perplexity/sonar
Web search
Ollama (Local)
ollama/llama3.1
Privacy-focused
Full list: OpenRouter Models
🚀 Usage
Start the Bot
# With virtual environment
source venv/bin/activate
python3 main.py

# Or using systemd (Linux)
sudo systemctl enable agentsclaw
sudo systemctl start agentsclaw
Telegram Commands
Command
Description
/start
Start bot & show menu
/help
Show all commands
/ai <prompt>
Ask AI anything
/cmd <command>
Execute terminal command
/file
File manager menu
/sys
System info dashboard
/model
Change AI model
/history
View conversation history
/clear
Clear chat history
/status
Bot status & uptime
Natural Language Examples
💬 "buat file hello.py dengan isi print('Hello World')"
💬 "install package numpy"
💬 "tampilkan info sistem"
💬 "cd /home && ls -la"
💬 "buat folder project baru"
AI-Powered Features
🤖 "buat script python untuk download gambar dari URL"
🤖 "debug error ini: [paste error]"
🤖 "convert json ke csv"
🤖 "buat dockerfile untuk flask app"
🤖 "optimize query SQL ini"
🛠️ Troubleshooting
Common Issues
Issue
Solution
ModuleNotFoundError
Run pip install -r requirements.txt
Invalid bot token
Check token with @BotFather
OpenRouter 401
Verify API key at openrouter.ai
Permission denied
Run with sudo or check file permissions
Command not found
Ensure binary is in PATH
Telegram timeout
Check internet connection
Logs & Debug
# View logs
tail -f logs/agentsclaw.log

# Debug mode
python3 main.py --debug

# Verbose output
python3 main.py -v
Support
📧 Email: support@agentsclaw.dev
💬 Telegram: @AgentsClawSupport
🐛 Issues: GitHub Issues
📁 Project Structure
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
🤝 Contributing
We welcome contributions! Please follow these steps:
Fork the repository
Clone your fork
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
Development Setup
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black bot/
flake8 bot/
Contributors
�
￼ 
📜 License
This project is licensed under the MIT License — see the LICENSE file for details.
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
SOFTWARE.
🙏 Acknowledgments
OpenRouter — Unified AI API Gateway
python-telegram-bot — Telegram Bot Framework
Termux — Android Terminal Emulator
Contributors — All amazing contributors
�
￼ 

�
Made with ❤️ by Agents Claw Team 
Telegram • GitHub • Website 
