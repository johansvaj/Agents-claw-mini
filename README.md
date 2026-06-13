<div align="center">

# 🦂 NEXCORIX CLAW

### Ultimate AI Agent Framework – Setara dengan NanoBot & PicoClaw

![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-0.25-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-purple?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Multi--Provider-red?style=for-the-badge)
![Memory](https://img.shields.io/badge/Memory-Vector%20%28Semantic%29-cyan?style=for-the-badge)
![MCP](https://img.shields.io/badge/MCP-Supported-orange?style=for-the-badge)

</div>

## 🎬 Demo

<p align="center">
<img src="./VID-20260609-WA0009.gif" width="100%">
</p>

## 🌌 Gambaran Umum

**Nexcorix Claw** adalah framework AI Agent modern yang menggabungkan kekuatan arsitektur **NanoBot** dan **PicoClaw**. Dirancang untuk membangun agen cerdas dengan:
- Memori jangka panjang berbasis vektor (semantic search)
- Workspace markdown (AGENTS.md, SOUL.md, USER.md, MEMORY.md)
- Sistem skill dari file `SKILL.md`
- Integrasi MCP (Model Context Protocol)
- WebUI workbench (FastAPI + WebSocket)
- Penjadwalan tugas (cron service)
- Manajemen izin (permission control)
- Multi-channel (Telegram, Discord, WhatsApp, Slack, Matrix, dll.)

## ✨ Fitur Lengkap

### 🤖 Inti AI (Agent Loop)
- **MessageBus** – antrian pesan async untuk komunikasi antar komponen
- **AgentLoop** – siklus utama AI (LLM → tool calling → memory)
- **ToolRegistry** – registrasi tools modular (`bash`, `read_file`, `write_file`, `mkdir`, `scan_network`, `install`)

### 🧠 Memori Cerdas
- **AdvancedMemory** – vector database (ChromaDB) + SQLite untuk fakta terstruktur
- Pencarian semantik (semantic search) dengan `all-MiniLM-L6-v2`
- Ekstraksi dan penyimpanan fakta (subject-predicate-object)
- Memori ringkasan (memory compaction) untuk percakapan panjang

### 📁 Workspace Markdown (File-as-DB)
- `AGENTS.md` – aturan perilaku agent
- `SOUL.md` – kepribadian, nada bicara, emoji
- `USER.md` – preferensi pengguna (nama, bahasa, zona waktu)
- `MEMORY.md` – catatan memori jangka panjang
- `TOOLS.md` – panduan penggunaan tools

### 🛠️ Skill System (Seperti PicoClaw)
- Simpan skill di `~/.nexcorix/skills/<nama>/SKILL.md`
- Format YAML frontmatter untuk metadata (`description`, `commands`)
- Muat skill secara dinamis dengan perintah `skill_load <nama>`

### 🔌 Integrasi MCP (Model Context Protocol)
- Klien MCP untuk terhubung ke server eksternal (Github, database, dll.)
- Daftar tools dari server tersedia otomatis

### 🌐 WebUI Workbench
- Antarmuka web modern dengan FastAPI + WebSocket
- Live chat, lihat workspace files, daftar tools, statistik memori
- URL: `http://localhost:18888`

### ⏰ Cron & Heartbeat (Otomatisasi)
- Jadwalkan tugas periodik (misal: backup memori setiap jam)
- Bisa ditambahkan melalui kode atau file konfigurasi

### 🔐 Manajemen Izin (Permissions)
- Kontrol akses per user ke tools: `read`, `write`, `bash`, `skills`, `web`
- Default untuk user lokal: semua izin diberikan

### 📱 Multi-Channel (25+ Platform)
- **Telegram** & **Discord** – fungsional penuh (isi token)
- **WhatsApp**, **Slack**, **Matrix**, **Teams**, **Gmail**, **Google Drive**, **GitHub**, **Notion**, **Trello**, **Jira**, **PostgreSQL**, **MySQL**, **Redis**, **n8n**, **Zapier**, **Home Assistant** – placeholder (siap dikembangkan)

### 🧰 Perintah Langsung (Tanpa API Key)
- `install nmap` – instal paket via apt/pkg/pip
- `scan network` – scan jaringan lokal (nmap/ping)
- `buat folder nama` – buat direktori
- `create file nama isi ...` – buat file dengan konten
- `run ls -la` – eksekusi perintah shell (streaming output)
- `web server` – jalankan HTTP server di port 8080

### ⚡ Performa & Keamanan
- Runtime cepat dengan asyncio
- Virtual environment terisolasi
- Eksekusi perintah dengan timeout
- Auto-repair struktur folder `modules/`

## 🚀 Quick Start (Cara Install & Jalankan)

> **Catatan**: Gunakan script `run.sh` (Linux/macOS/Termux) atau `run.bat` (Windows). Script akan otomatis:
> - mendeteksi Python ≥ 3.8
> - membuat virtual environment `venv`
> - menginstall dependensi minimal (requests, urllib3)
> - menanyakan apakah ingin install library advanced (chromadb, fastapi, dll)
> - menjalankan `nexcorix_claw.py`

### Windows
```cmd
git clone https://github.com/johansvaj/Nexorix-claw.git
cd Nexorix-claw
run.bat
```

Linux / macOS / Termux

```bash
git clone https://github.com/johansvaj/Nexorix-claw.git
cd Nexorix-claw
chmod +x run.sh
./run.sh
```

Jika ingin langsung install semua library (advanced) tanpa tanya:

```bash
./run.sh --full
```

Alternatif Manual (tanpa script)

```bash
# Buat virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# atau
venv\Scripts\activate     # Windows

# Install dependensi minimal
pip install requests urllib3

# (Opsional) Install advanced
pip install chromadb sentence-transformers fastapi uvicorn python-telegram-bot discord.py schedule pyyaml

# Jalankan program
python nexcorix_claw.py
```

🎯 Penggunaan (Menu Utama)

Setelah program berjalan, Anda akan melihat menu dengan 20 pilihan:

No Fungsi Keterangan
1 Dashboard Lihat status AI, memori, skill, channel
2 Chat Mode interaktif (ketik perintah langsung)
3 Models Ganti model AI (Settings → 2)
4 Agents Subagent (coming soon)
5 Memory Lihat dan kelola memori
6 Skills Lihat dan buat skill baru
7 Tools Daftar tools yang tersedia
8 Channels Konfigurasi 25 channel (Telegram, Discord, dll.)
9 WebUI Buka antarmuka web (http://localhost:18888)
10 Automation Cron service (otomatisasi)
11 Workspace Lihat folder workspace (~/.nexcorix/workspace)
12 API Keys Atur API key untuk AI (OpenRouter, OpenAI, dll.)
13-19 Lainnya (placeholder)
20 Exit Keluar program

Contoh Chat

```
> scan network
> install nmap
> buat folder proyek
> create file test.py isi print("Hello")
> run ls -la
> halo
> apa kabar
> bantu buat script python (butuh API key)
```

🌐 Model AI yang Didukung (100+)

· OpenRouter – openai/gpt-3.5-turbo, openai/gpt-4o, anthropic/claude-3.5-sonnet, google/gemini-1.5-flash, deepseek/deepseek-chat, meta-llama/llama-3.1-8b-instruct, dll.
· OpenAI – gpt-4o, gpt-4-turbo, gpt-3.5-turbo
· Anthropic – claude-3.5-sonnet, claude-3-haiku
· Google – gemini-1.5-pro, gemini-1.5-flash
· DeepSeek – deepseek-chat, deepseek-coder
· Local (Ollama) – dukungan penuh

Ganti model di Settings (18) → Current Model (2).

📁 Struktur Proyek

```
Nexorix-claw/
├── nexcorix_claw.py          # Entry point utama
├── modules/                  # Modul modular (advanced_memory, workspace_v2, dll)
│   ├── advanced_memory.py
│   ├── workspace_v2.py
│   ├── skill_loader.py
│   ├── mcp_client_v2.py
│   ├── webui_server.py
│   ├── cron_service.py
│   ├── permissions.py
│   ├── message_bus.py
│   ├── agent_loop.py
│   ├── tool_registry_v2.py
│   └── llm_provider.py
├── run.sh / run.bat          # Launcher universal (auto venv & install)
├── requirements.txt          (opsional)
└── README.md
```

🛠️ Konfigurasi

API Key

1. Jalankan program → menu 18 Settings → 5 API Keys → pilih provider (1 untuk OpenRouter)
2. Masukkan API key (dapatkan dari openrouter.ai/keys)

Channel Telegram

1. Menu 8 Channels → c → pilih nomor 1 (Telegram)
2. Masukkan bot token (dari @BotFather) dan admin ID (opsional)
3. s untuk start

Workspace Customization

· Edit file di ~/.nexcorix/workspace/ untuk mengubah:
  · AGENTS.md – aturan
  · SOUL.md – kepribadian
  · USER.md – preferensi
  · MEMORY.md – memori (akan diisi otomatis)

📈 Roadmap

· Core runtime & auto-repair
· Multi-channel (25 platform)
· Advanced memory (vector DB)
· Workspace markdown (file-as-DB)
· Skill system (SKILL.md)
· MCP client
· WebUI workbench
· Cron service
· Permission manager
· Visual workflow builder
· Mobile dashboard
· Plugin marketplace

🤝 Kontribusi

```bash
fork → clone → branch → code → commit → push → pull request
```

Kontribusi selalu diterima. Silakan buat issue atau pull request di GitHub.

📜 Lisensi

MIT License – bebas digunakan, dimodifikasi, dan didistribusikan.

---

<div align="center">

🦂 NEXCORIX CLAW

Create • Automate • Innovate

Version 0.25 – Built For The Future

</div>
