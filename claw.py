#!/usr/bin/env python3
"""
🤖⚡ Agents Claw Mini v6.0 - AI Terminal Controller via Telegram
AI punya akses penuh terminal: coding, install tools, run commands, manage files
"""

import os
import json
import asyncio
import time
import subprocess
import re
from pathlib import Path

CONFIG_FILE = os.path.expanduser("~/.claw_config.json")
PROJECTS_DIR = os.path.expanduser("~/ClawProjects")

COLORS = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m",
    "white": "\033[97m", "orange": "\033[38;5;208m",
}

def color(name):
    return COLORS.get(name, "")

def clear():
    os.system("clear")

def sep(w=60):
    return color("cyan") + "  ═" + "═" * w + "═  " + color("reset")

def header():
    return "\n".join([
        "",
        color("cyan") + "  ╔" + "═" * 62 + "╗" + color("reset"),
        color("cyan") + "  ║" + color("bold") + color("yellow") + "       🤖⚡  A G E N T S   C L A W   M I N I  ⚡🤖       " + color("reset") + color("cyan") + "║",
        color("cyan") + "  ║" + color("dim") + "         AI Terminal Controller via Telegram v6.0        " + color("reset") + color("cyan") + "║",
        color("cyan") + "  ╚" + "═" * 62 + "╝" + color("reset"),
        "",
    ])

def menu_item(num, icon, text, desc, clr="white"):
    return "     " + color("bold") + color("yellow") + "[" + num + "]" + color("reset") + " " + color(clr) + icon + color("reset") + "  " + color("bold") + text + color("reset") + "\n        " + color("dim") + desc + color("reset")

# ============================================
# PROVIDERS & MODELS
# ============================================

PROVIDERS = {
    "1": {"name": "OpenAI", "icon": "🅾️", "color": "green", "online": True,
        "models": {"1": ("openai/gpt-4o", "GPT-4o", "🌟"), "2": ("openai/gpt-4o-mini", "GPT-4o Mini", "⭐"), "3": ("openai/gpt-4-turbo", "GPT-4 Turbo", "💎")}},
    "2": {"name": "Anthropic", "icon": "🅰️", "color": "magenta", "online": True,
        "models": {"1": ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet", "🎭"), "2": ("anthropic/claude-3-opus", "Claude 3 Opus", "👑")}},
    "3": {"name": "Google", "icon": "🅶️", "color": "blue", "online": True,
        "models": {"1": ("google/gemini-1.5-pro", "Gemini 1.5 Pro", "🔮"), "2": ("google/gemini-1.5-flash", "Gemini 1.5 Flash", "⚡")}},
    "4": {"name": "DeepSeek", "icon": "🐋", "color": "cyan", "online": True,
        "models": {"1": ("deepseek/deepseek-chat", "DeepSeek Chat", "🧠"), "2": ("deepseek/deepseek-coder", "DeepSeek Coder", "💻"), "3": ("deepseek/deepseek-r1", "DeepSeek R1", "🔥")}},
    "5": {"name": "Meta", "icon": "Ⓜ️", "color": "blue", "online": True,
        "models": {"1": ("meta-llama/llama-3.1-70b-instruct", "Llama 3.1 70B", "🦙"), "2": ("meta-llama/llama-3.1-8b-instruct", "Llama 3.1 8B", "🐑")}},
    "6": {"name": "Qwen", "icon": "🇶", "color": "yellow", "online": True,
        "models": {"1": ("qwen/qwen-2.5-72b-instruct", "Qwen 2.5 72B", "🐉")}},
    "7": {"name": "Mistral", "icon": "Ⓜ️", "color": "orange", "online": True,
        "models": {"1": ("mistralai/mistral-large", "Mistral Large", "🌊")}},
    "8": {"name": "Kimi", "icon": "🌙", "color": "white", "online": True,
        "models": {"1": ("moonshotai/kimi-k2-5", "Kimi K2.5", "🌙")}},
    "9": {"name": "Perplexity", "icon": "🔍", "color": "green", "online": True,
        "models": {"1": ("perplexity/llama-3.1-sonar-large-128k-online", "Sonar Large", "🔍")}},
    "10": {"name": "Others", "icon": "✨", "color": "white", "online": True,
        "models": {"1": ("microsoft/wizardlm-2-8x22b", "WizardLM 2", "🧙")}},
    "11": {"name": "Ollama", "icon": "💻", "color": "green", "online": False,
        "models": {"1": ("llama3.1", "Llama 3.1", "🦙"), "2": ("mistral", "Mistral", "🌊"), "3": ("qwen2.5", "Qwen 2.5", "🐉"), "4": ("codellama", "CodeLlama", "💻")}},
}

MODELS = {}

def build_models():
    for pid, prov in PROVIDERS.items():
        for mid, (aid, name, icon) in prov["models"].items():
            MODELS[pid + "_" + mid] = {"id": aid, "name": name, "icon": icon, "provider": prov["name"], "online": prov["online"]}

build_models()

# ============================================
# CONFIG
# ============================================

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"token": "", "openrouter_key": "", "model": "4_2", "admin_id": "", "system": "Kamu AI assistant."}

def save_cfg(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    print(color("green") + "\n    💾 Tersimpan!" + color("reset"))

# ============================================
# SELECT MODEL
# ============================================

def select_model():
    while True:
        clear(); print(header())
        print(color("bold") + color("yellow") + "    🌐 PILIH PROVIDER" + color("reset")); print(sep())
        for pid, p in PROVIDERS.items():
            print("    [" + color("yellow") + pid + color("reset") + "] " + p["icon"] + " " + color(p["color"]) + p["name"] + color("reset") + " " + color("dim") + ("🌐 Online" if p["online"] else "💻 Offline") + color("reset"))
        print("\n    " + color("dim") + "0. Kembali" + color("reset"))
        prov = input("\n    Pilih [0-11]: ").strip()
        if prov == "0": return None
        if prov not in PROVIDERS: continue
        
        while True:
            clear(); print(header())
            print(color("bold") + color("yellow") + "    🤖 " + PROVIDERS[prov]["name"] + color("reset")); print(sep())
            for mid, (aid, name, icon) in PROVIDERS[prov]["models"].items():
                print("    [" + color("yellow") + mid + color("reset") + "] " + icon + " " + name)
            print("\n    " + color("dim") + "0. Kembali" + color("reset"))
            model = input("\n    Pilih: ").strip()
            if model == "0": break
            if model in PROVIDERS[prov]["models"]:
                fid = prov + "_" + model
                print("\n    " + color("green") + "✅ " + MODELS[fid]["icon"] + " " + MODELS[fid]["name"] + color("reset"))
                time.sleep(1); return fid
    return None

# ============================================
# SETTINGS
# ============================================

def setting():
    cfg = load_cfg()
    new_model = select_model()
    if new_model: cfg["model"] = new_model
    
    clear(); print(header()); print(color("bold") + "    🔑 SETUP" + color("reset")); print(sep())
    
    t = input("\n    Telegram Token (dari @BotFather): ").strip()
    if t: cfg["token"] = t; print("    " + color("green") + "✅ Token OK" + color("reset"))
    
    m = MODELS.get(cfg.get("model", "4_2"), {})
    if m.get("online"):
        k = input("\n    OpenRouter Key: ").strip()
        if k: cfg["openrouter_key"] = k; print("    " + color("green") + "✅ Key OK" + color("reset"))
    
    a = input("\n    Admin Telegram ID: ").strip()
    if a: cfg["admin_id"] = a; print("    " + color("green") + "✅ Admin OK" + color("reset"))
    
    save_cfg(cfg)
    input("\n    " + color("dim") + "Enter..." + color("reset"))

def lihat():
    cfg = load_cfg(); clear(); print(header()); print(color("bold") + "    📋 KONFIG" + color("reset")); print(sep())
    m = MODELS.get(cfg.get("model", "4_2"), {})
    print(f"\n    Model: {m.get('icon','')} {m.get('name','?')} [{m.get('provider','?')}]")
    print(f"    Token: {cfg.get('token','')[:20]}...")
    print(f"    Key: {cfg.get('openrouter_key','')[:20]}...")
    print(f"    Admin: {cfg.get('admin_id') or '❌'}")
    input("\n    Enter...")

async def test_ai():
    cfg = load_cfg(); m = MODELS.get(cfg.get("model", "4_2"))
    clear(); print(header()); print(color("bold") + "    🧪 TEST" + color("reset")); print(sep())
    if not m.get("online"): print("Offline skip"); return
    if not cfg.get("openrouter_key"): print("Key belum set"); return
    try:
        import aiohttp
        async with aiohttp.ClientSession() as s:
            async with s.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + cfg["openrouter_key"], "Content-Type": "application/json", "HTTP-Referer": "https://t.me", "X-Title": "Claw"},
                json={"model": m["id"], "messages": [{"role": "user", "content": "Halo!"}], "max_tokens": 50}
            ) as r:
                d = await r.json()
                if r.status == 200:
                    print(f"\n    {color('green')}✅ OK: {d['choices'][0]['message']['content'][:50]}...{color('reset')}")
                else: print(f"\n    ❌ {d}")
    except Exception as e: print(f"\n    ❌ {e}")

def test():
    asyncio.run(test_ai())
    input("\n    Enter...")

# ============================================
# MAIN: TELEGRAM BOT WITH FULL TERMINAL ACCESS
# ============================================

def jalankan():
    cfg = load_cfg()
    m = MODELS.get(cfg.get("model", "4_2"))
    
    if not cfg.get("token"):
        clear(); print(header()); print(f"\n    {color('red')}❌ Token belum di-set!{color('reset')}"); input("    Enter..."); return
    if m.get("online") and not cfg.get("openrouter_key"):
        clear(); print(header()); print(f"\n    {color('red')}❌ Key belum di-set!{color('reset')}"); input("    Enter..."); return
    
    clear(); print(header()); print(color("bold") + color("green") + "    🚀 BOT JALAN!" + color("reset")); print(sep())
    print(f"\n    🤖 {m.get('icon','')} {m.get('name','')} | {m.get('provider','')}")
    print(f"    💻 AI punya AKSES PENUH terminal")
    print(f"    📁 Project: {PROJECTS_DIR}")
    print(f"\n    {color('dim')}Ctrl+C stop{color('reset')}\n")
    
    # Buat bot script
    bot_code = '''#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import subprocess
import re
import time
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "''' + cfg["token"] + '''"
API_KEY = "''' + cfg.get("openrouter_key", "") + '''"
MODEL = "''' + m["id"] + '''"
ADMIN_ID = "''' + cfg.get("admin_id", "") + '''"
PROJECTS_DIR = os.path.expanduser("~/ClawProjects")

os.makedirs(PROJECTS_DIR, exist_ok=True)

# ============================================
# AI CHAT
# ============================================

async def ai_chat(messages, temperature=0.7):
    async with aiohttp.ClientSession() as s:
        async with s.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json", "HTTP-Referer": "https://t.me", "X-Title": "ClawTerminal"},
            json={"model": MODEL, "messages": messages, "temperature": temperature}
        ) as r:
            return await r.json()

# ============================================
# TERMINAL EXECUTOR
# ============================================

def run_command(cmd, cwd=None, timeout=60):
    """Jalankan command di terminal"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, 
            cwd=cwd or os.path.expanduser("~"), timeout=timeout
        )
        output = result.stdout if result.stdout else "(no output)"
        if result.stderr:
            output += "\\n⚠️ STDERR:\\n" + result.stderr
        return output[:3900], result.returncode
    except subprocess.TimeoutExpired:
        return "⏱️ Timeout! Command terlalu lama.", 1
    except Exception as e:
        return f"❌ Error: {str(e)}", 1

def run_sudo_command(cmd, password=None, timeout=60):
    """Jalankan command dengan sudo"""
    if password:
        full_cmd = f'echo "{password}" | sudo -S ' + cmd
    else:
        full_cmd = "sudo " + cmd
    return run_command(full_cmd, timeout=timeout)

# ============================================
# FILE MANAGER
# ============================================

def save_file(filepath, content):
    """Simpan file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        return True, f"✅ File tersimpan: {filepath}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def read_file(filepath):
    """Baca file"""
    try:
        with open(filepath, "r") as f:
            return True, f.read()
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def list_dir(path):
    """List direktori"""
    try:
        items = os.listdir(path)
        result = f"📁 {path}\\n\\n"
        for item in sorted(items):
            full = os.path.join(path, item)
            if os.path.isdir(full):
                result += f"📂 {item}/\\n"
            else:
                size = os.path.getsize(full)
                result += f"📄 {item} ({size} bytes)\\n"
        return True, result
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# ============================================
# DETECT LANGUAGE
# ============================================

LANG_MAP = {
    "python": (".py", "python3"), "py": (".py", "python3"),
    "bash": (".sh", "bash"), "sh": (".sh", "bash"), "shell": (".sh", "bash"),
    "javascript": (".js", "node"), "js": (".js", "node"),
    "html": (".html", "open"), "css": (".css", "cat"),
    "c": (".c", "gcc"), "cpp": (".cpp", "g++"), "c++": (".cpp", "g++"),
    "java": (".java", "javac"), "go": (".go", "go run"), "golang": (".go", "go run"),
    "rust": (".rs", "rustc"), "rs": (".rs", "rustc"),
    "php": (".php", "php"), "ruby": (".rb", "ruby"), "rb": (".rb", "ruby"),
    "perl": (".pl", "perl"), "pl": (".pl", "perl"),
    "lua": (".lua", "lua"), "sql": (".sql", "sqlite3"),
    "json": (".json", "cat"), "yaml": (".yaml", "cat"), "xml": (".xml", "cat"),
    "dockerfile": ("Dockerfile", "docker"), "docker": ("Dockerfile", "docker"),
    "nginx": (".conf", "nginx"), "apache": (".conf", "apache2"),
}

def detect_language(text):
    """Deteksi bahasa pemrograman dari teks"""
    text_lower = text.lower()
    
    # Cari mention bahasa spesifik
    for lang, (ext, runner) in LANG_MAP.items():
        if lang in text_lower:
            return lang, ext, runner
    
    # Cari pola file
    if ".py" in text_lower or "python" in text_lower:
        return "python", ".py", "python3"
    if ".sh" in text_lower or "bash" in text_lower or "shell" in text_lower:
        return "bash", ".sh", "bash"
    if ".js" in text_lower or "javascript" in text_lower or "node" in text_lower:
        return "javascript", ".js", "node"
    if ".html" in text_lower or "website" in text_lower or "web" in text_lower:
        return "html", ".html", "open"
    if ".c" in text_lower and "cpp" not in text_lower and "c++" not in text_lower:
        return "c", ".c", "gcc"
    if ".cpp" in text_lower or "c++" in text_lower:
        return "cpp", ".cpp", "g++"
    if ".java" in text_lower:
        return "java", ".java", "javac"
    if ".go" in text_lower or "golang" in text_lower:
        return "go", ".go", "go run"
    if ".rs" in text_lower or "rust" in text_lower:
        return "rust", ".rs", "rustc"
    if ".php" in text_lower:
        return "php", ".php", "php"
    if ".rb" in text_lower or "ruby" in text_lower:
        return "ruby", ".rb", "ruby"
    
    return "python", ".py", "python3"  # Default

# ============================================
# AI SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """Kamu adalah AI Terminal Controller untuk Kali NetHunter.
User mengontrol terminal via Telegram. Kamu bisa:
1. Buat kode SEMUA bahasa pemrograman
2. Install tools (apt, pip, npm, dll)
3. Jalankan command terminal
4. Manage file & folder
5. Scan network, exploit, dll (untuk pentesting)

FORMAT RESPONS:
- Untuk coding: langsung kode MURNI, tanpa markdown ```
- Untuk command: tulis command yang bisa di-copy paste
- Untuk install: berikan command apt/pip/npm
- Untuk file multi: gunakan marker === FILE: nama ===

Jika user minta "buat script X", generate kode lengkap.
Jika user minta "install X", berikan command instalasi.
Jika user minta "scan X", berikan command nmap/masscan.
Jika user minta "hack X" atau "exploit X", berikan tools & command yang sesuai (educational only).

Bahasa: Indonesia/English otomatis."""

# ============================================
# TELEGRAM HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    await update.message.reply_text(
        f"""🤖 *Agents Claw Mini - AI Terminal*

👤 Info Kamu:
🆔 ID: `{u.id}`
📛 Nama: {u.first_name}

💻 *AI Terminal Commands:*
• `buat python script port scanner`
• `buat bash script backup otomatis`
• `buat website html css js`
• `install nmap metasploit`
• `scan 192.168.1.1 dengan nmap`
• `buat folder project baru`
• `list file di /root`
• `jalankan command: ls -la`
• `buat c program kalkulator`
• `buat rust tool brute force`

🌍 Support: Python, Bash, JS, C, C++, Java, Go, Rust, PHP, Ruby, Perl, Lua, SQL, HTML, DLL

Kirim perintah apa saja!""",
        parse_mode="Markdown"
    )

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    await update.message.reply_text(f"🆔 ID: `{u.id}`\\n👤 {u.first_name}", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    text = update.message.text
    chat_id = update.effective_chat.id
    
    if u.is_bot:
        return
    
    print(f"[{u.username or u.first_name}] (ID:{u.id}): {text[:80]}")
    
    # Cek admin
    is_admin = (str(u.id) == ADMIN_ID) if ADMIN_ID else True
    
    # Pattern detection
    text_lower = text.lower()
    
    # === PATTERN: Install tools ===
    if any(k in text_lower for k in ["install", "pasang", "apt install", "pip install", "npm install"]):
        await handle_install(update, text)
        return
    
    # === PATTERN: Run command ===
    if any(k in text_lower for k in ["jalankan", "run", "execute", "command:", "cmd:", "terminal:"]):
        await handle_command(update, text, is_admin)
        return
    
    # === PATTERN: List files ===
    if any(k in text_lower for k in ["list file", "lihat file", "ls ", "dir ", "folder "]):
        await handle_list(update, text)
        return
    
    # === PATTERN: Read file ===
    if any(k in text_lower for k in ["baca file", "read file", "cat file", "lihat isi"]):
        await handle_read(update, text)
        return
    
    # === PATTERN: Coding / Buat script ===
    if any(k in text_lower for k in ["buat", "create", "script", "program", "kode", "code", "generate", "coding"]):
        await handle_coding(update, text)
        return
    
    # === DEFAULT: AI Chat ===
    await handle_chat(update, text)

async def handle_install(update, text):
    """Handle permintaan install tools"""
    wait = await update.message.reply_text("📦 Mempersiapkan instalasi...")
    
    # Extract package names
    text_lower = text.lower()
    packages = []
    
    # Parse dari command
    if "apt install" in text_lower:
        parts = text_lower.split("apt install")
        if len(parts) > 1:
            packages = parts[1].strip().split()
    elif "pip install" in text_lower:
        parts = text_lower.split("pip install")
        if len(parts) > 1:
            packages = parts[1].strip().split()
    elif "npm install" in text_lower or "npm i " in text_lower:
        parts = text_lower.split("npm install") if "npm install" in text_lower else text_lower.split("npm i ")
        if len(parts) > 1:
            packages = parts[1].strip().split()
    else:
        # AI suggest install command
        messages = [
            {"role": "system", "content": "Kamu package manager assistant. User mau install tool. Berikan command instalasi yang tepat untuk Kali Linux."},
            {"role": "user", "content": text}
        ]
        try:
            result = await ai_chat(messages, temperature=0.3)
            cmd = result["choices"][0]["message"]["content"].replace("```bash", "").replace("```", "").strip()
            
            await wait.edit_text(f"📦 *Command Install:*\\n```bash\\n{cmd}\\n```\\n\\n⏳ Menjalankan...", parse_mode="Markdown")
            
            output, code = run_command(cmd, timeout=120)
            status = "✅" if code == 0 else "⚠️"
            
            await update.message.reply_text(
                f"{status} *Hasil Instalasi:*\\n```\\n{output[:3900]}\\n```",
                parse_mode="Markdown"
            )
            return
        except Exception as e:
            await wait.edit_text(f"❌ Error: {str(e)[:200]}")
            return
    
    # Direct install
    if packages:
        cmd = f"apt update && apt install -y {' '.join(packages)}"
        await wait.edit_text(f"📦 *Installing:* `{' '.join(packages)}`\\n⏳ Mohon tunggu...", parse_mode="Markdown")
        
        output, code = run_command(cmd, timeout=300)
        status = "✅" if code == 0 else "⚠️"
        
        await update.message.reply_text(
            f"{status} *Hasil:*\\n```\\n{output[:3900]}\\n```",
            parse_mode="Markdown"
        )

async def handle_command(update, text, is_admin):
    """Handle eksekusi command"""
    # Extract command
    patterns = [
        r'(?:jalankan|run|execute)\s+(?:command\s+)?[:"]?\s*(.+)',
        r'(?:cmd|command|terminal):\s*(.+)',
    ]
    
    cmd = None
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            cmd = match.group(1).strip()
            break
    
    if not cmd:
        # Ambil setelah keyword
        for keyword in ["jalankan ", "run ", "execute "]:
            if keyword in text.lower():
                idx = text.lower().find(keyword) + len(keyword)
                cmd = text[idx:].strip()
                break
    
    if not cmd:
        await update.message.reply_text("❌ Command tidak terdeteksi. Format: `jalankan command: ls -la`")
        return
    
    # Warning untuk command berbahaya
    dangerous = ["rm -rf /", "mkfs", "dd if=", ":(){:|:&};:", "del /f /s"]
    if any(d in cmd for d in dangerous):
        await update.message.reply_text("🚫 *Command berbahaya terdeteksi!* Dibatalkan untuk keamanan.", parse_mode="Markdown")
        return
    
    wait = await update.message.reply_text(f"💻 *Executing:*\\n```bash\\n{cmd}\\n```", parse_mode="Markdown")
    
    output, code = run_command(cmd, timeout=60)
    status = "✅" if code == 0 else "⚠️"
    
    await update.message.reply_text(
        f"{status} *Output:*\\n```\\n{output[:3900]}\\n```",
        parse_mode="Markdown"
    )

async def handle_list(update, text):
    """Handle list direktori"""
    # Extract path
    patterns = [
        r'(?:list|lihat|ls)\s+(?:file\s+)?(?:di\s+)?(?:folder\s+)?["\\']?(.+?)["\\']?(?:\s|$)',
        r'(?:dir|folder)\s+["\\']?(.+?)["\\']?',
    ]
    
    path = os.path.expanduser("~")
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            potential = match.group(1).strip()
            if potential and not potential.startswith("file"):
                path = os.path.expanduser(potential)
                break
    
    if not os.path.exists(path):
        await update.message.reply_text(f"❌ Path tidak ditemukan: `{path}`", parse_mode="Markdown")
        return
    
    ok, result = list_dir(path)
    if ok:
        await update.message.reply_text(f"```{result[:4000]}```", parse_mode="Markdown")
    else:
        await update.message.reply_text(result)

async def handle_read(update, text):
    """Handle baca file"""
    # Extract filepath
    patterns = [
        r'(?:baca|read|cat|lihat\s+isi)\s+(?:file\s+)?["\\']?(.+?)["\\']?(?:\s|$)',
    ]
    
    filepath = None
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            filepath = os.path.expanduser(match.group(1).strip())
            break
    
    if not filepath or not os.path.exists(filepath):
        await update.message.reply_text("❌ File tidak ditemukan.")
        return
    
    ok, content = read_file(filepath)
    if ok:
        ext = os.path.splitext(filepath)[1]
        lang_map = {".py": "python", ".sh": "bash", ".js": "javascript", ".html": "html", ".c": "c", ".cpp": "cpp", ".java": "java", ".go": "go", ".rs": "rust", ".php": "php", ".rb": "ruby", ".sql": "sql"}
        lang = lang_map.get(ext, "")
        
        if len(content) > 4000:
            # Kirim sebagai file
            await update.message.reply_document(
                document=open(filepath, "rb"),
                caption=f"📄 `{os.path.basename(filepath)}` ({len(content)} bytes)",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"📄 `{os.path.basename(filepath)}`:\\n```{lang}\\n{content[:3900]}\\n```",
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text(content)

async def handle_coding(update, text):
    """Handle coding - generate & save & execute"""
    wait = await update.message.reply_text("🤖 AI sedang generate kode...")
    
    try:
        # Deteksi bahasa
        lang, ext, runner = detect_language(text)
        
        # Extract folder name
        folder_match = re.search(r'(?:folder|project|directory|di)\s+["\\']?(\w+)["\\']?', text.lower())
        folder = folder_match.group(1) if folder_match else f"project_{int(time.time())}"
        
        # Extract filename
        filename_match = re.search(r'(?:nama\s+file|file\s+name|simpan\s+sebagai)\s+["\\']?(\w+)["\\']?', text.lower())
        filename = (filename_match.group(1) if filename_match else "script") + ext
        
        # AI generate
        messages = [
            {"role": "system", "content": f"""Kamu programmer {lang} expert. 
Buat kode lengkap sesuai permintaan user. 
HANYA kode, tanpa penjelasan, tanpa markdown ```.
Jika perlu multi-file, gunakan marker:
=== FILE: namafile.ext ===
[kode]
=== END FILE ==="""},
            {"role": "user", "content": text}
        ]
        
        result = await ai_chat(messages, temperature=0.3)
        raw_code = result["choices"][0]["message"]["content"]
        
        # Bersihkan
        raw_code = raw_code.replace("```python", "").replace("```bash", "").replace("```javascript", "").replace("```" + lang, "").replace("```", "").strip()
        
        # Parse multi-file atau single
        base_path = os.path.join(PROJECTS_DIR, folder)
        os.makedirs(base_path, exist_ok=True)
        
        files_created = []
        
        if "=== FILE:" in raw_code:
            # Multi-file
            current_file = None
            content_lines = []
            
            for line in raw_code.split("\\n"):
                if line.startswith("=== FILE:"):
                    if current_file and content_lines:
                        fp = os.path.join(base_path, current_file)
                        with open(fp, "w") as f:
                            f.write("\\n".join(content_lines))
                        files_created.append(fp)
                        content_lines = []
                    current_file = line.replace("=== FILE:", "").strip()
                elif line.startswith("=== END FILE"):
                    if current_file and content_lines:
                        fp = os.path.join(base_path, current_file)
                        with open(fp, "w") as f:
                            f.write("\\n".join(content_lines))
                        files_created.append(fp)
                        content_lines = []
                        current_file = None
                else:
                    if current_file is not None:
                        content_lines.append(line)
            
            if current_file and content_lines:
                fp = os.path.join(base_path, current_file)
                with open(fp, "w") as f:
                    f.write("\\n".join(content_lines))
                files_created.append(fp)
        else:
            # Single file
            fp = os.path.join(base_path, filename)
            with open(fp, "w") as f:
                f.write(raw_code)
            files_created.append(fp)
        
        # Info ke user
        file_list = "\\n".join([f"📄 `{os.path.basename(f)}`" for f in files_created])
        rel_path = base_path.replace(os.path.expanduser("~"), "~")
        
        await wait.edit_text(
            f"✅ *Kode {lang.upper()} Generated!*\\n\\n"
            f"📁 Folder: `{rel_path}`\\n"
            f"{file_list}\\n\\n"
            f"⏳ Menjalankan...",
            parse_mode="Markdown"
        )
        
        # Execute
        if len(files_created) == 1:
            main_file = files_created[0]
            
            # Compile kalau perlu
            if lang == "c":
                compile_cmd = f"gcc '{main_file}' -o '{main_file.replace('.c', '')}'"
                run_command(compile_cmd)
                run_cmd = f"'{main_file.replace('.c', '')}'"
            elif lang == "cpp":
                compile_cmd = f"g++ '{main_file}' -o '{main_file.replace('.cpp', '')}'"
                run_command(compile_cmd)
                run_cmd = f"'{main_file.replace('.cpp', '')}'"
            elif lang == "java":
                compile_cmd = f"javac '{main_file}'"
                run_command(compile_cmd)
                class_name = os.path.basename(main_file).replace(".java", "")
                run_cmd = f"cd '{base_path}' && java {class_name}"
            elif lang == "rust":
                compile_cmd = f"rustc '{main_file}' -o '{main_file.replace('.rs', '')}'"
                run_command(compile_cmd)
                run_cmd = f"'{main_file.replace('.rs', '')}'"
            elif lang == "go":
                run_cmd = f"go run '{main_file}'"
            else:
                run_cmd = f"{runner} '{main_file}'"
            
            output, code = run_command(run_cmd, cwd=base_path, timeout=30)
            status = "✅" if code == 0 else "⚠️"
            
            # Kirim output
            if len(output) > 4000:
                # Simpan ke file dan kirim
                out_file = os.path.join(base_path, "output.txt")
                with open(out_file, "w") as f:
                    f.write(output)
                await update.message.reply_document(
                    document=open(out_file, "rb"),
                    caption=f"{status} *Output ({len(output)} chars):*"
                )
            else:
                await update.message.reply_text(
                    f"{status} *Output:*\\n```\\n{output[:3900]}\\n```",
                    parse_mode="Markdown"
                )
            
            # Kirim file source
            await update.message.reply_document(
                document=open(main_file, "rb"),
                caption=f"📎 Source: `{os.path.basename(main_file)}`",
                parse_mode="Markdown"
            )
            
        else:
            # Multi-file project
            await update.message.reply_text(
                f"📦 *Multi-file project dibuat!*\\n\\n"
                f"📁 `{rel_path}`\\n"
                f"Total: {len(files_created)} files\\n\\n"
                f"Untuk jalankan, masuk folder lalu run manual.",
                parse_mode="Markdown"
            )
            
            # Kirim semua file sebagai zip kalau banyak
            if len(files_created) > 3:
                zip_path = os.path.join(PROJECTS_DIR, f"{folder}.zip")
                run_command(f"cd '{PROJECTS_DIR}' && zip -r '{folder}.zip' '{folder}'")
                if os.path.exists(zip_path):
                    await update.message.reply_document(
                        document=open(zip_path, "rb"),
                        caption=f"📦 `{folder}.zip`"
                    )
    
    except Exception as e:
        await wait.edit_text(f"❌ Error: {str(e)[:400]}")
        print(f"Coding error: {e}")

async def handle_chat(update, text):
    """Handle chat biasa dengan AI"""
    wait = await update.message.reply_text("🤔 Mikir...")
    
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
        
        result = await ai_chat(messages)
        response = result["choices"][0]["message"]["content"]
        
        # Cek kalau respons berisi command
        if "```bash" in response or "```sh" in response:
            # Extract command
            cmd_match = re.search(r'```(?:bash|sh)\\n(.+?)\\n```', response, re.DOTALL)
            if cmd_match:
                cmd = cmd_match.group(1).strip()
                # Tanya user mau jalankan?
                await wait.edit_text(
                    f"🤖 *AI Response:*\\n\\n{response[:2000]}\\n\\n"
                    f"💻 *Jalankan command ini?*\\n"
                    f"Ketik: `ya` untuk jalankan",
                    parse_mode="Markdown"
                )
                # Simpan command untuk ditunggu
                # (Simplified: langsung kirim saja)
                return
        
        await wait.edit_text(response[:4096])
        
    except Exception as e:
        await wait.edit_text(f"❌ Error: {str(e)[:200]}")

# ============================================
# MAIN
# ============================================

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", id_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("✅ BOT JALAN!")
print(f"Model: {MODEL}")
print("AI Terminal Controller aktif!")
print("Kirim /start ke bot")
app.run_polling()
'''
    
    with open("/tmp/claw_bot.py", "w") as f:
        f.write(bot_code)
    
    os.system("python3 /tmp/claw_bot.py")

# ============================================
# MENU UTAMA
# ============================================

def main():
    while True:
        clear(); print(header())
        
        cfg = load_cfg()
        m = MODELS.get(cfg.get("model", "4_2"), {})
        
        token_ok = cfg.get("token") != ""
        key_ok = cfg.get("openrouter_key") != "" or not m.get("online", True)
        ready = token_ok and key_ok
        
        status = color("green") + "READY ✅" if ready else color("red") + "SETUP REQUIRED ⚠️"
        
        print("    " + color("bold") + "Status: " + status + color("reset"))
        print("    " + color("dim") + "Model: " + m.get("icon", "") + " " + m.get("name", "Not Set") + color("reset"))
        print("    " + color("dim") + "Mode: AI Terminal Controller via Telegram" + color("reset"))
        print("")
        
        print(menu_item("1", "🚀", "JALANKAN BOT", "Start AI Terminal Bot di Telegram", "green"))
        print(menu_item("2", "⚙️ ", "SETING", "Pilih model, token, API key", "yellow"))
        print(menu_item("3", "📋", "LIHAT SETING", "Tampilkan konfigurasi", "blue"))
        print(menu_item("4", "🧪", "TEST KONEKSI", "Cek AI connection", "magenta"))
        print(menu_item("5", "❌", "KELUAR", "Tutup launcher", "red"))
        print("")
        
        p = input("    " + color("bold") + color("yellow") + "➤ Pilih [1-5]: " + color("reset")).strip()
        
        if p == "1": jalankan()
        elif p == "2": setting()
        elif p == "3": lihat()
        elif p == "4": test()
        elif p == "5":
            clear(); print(header())
            print(f"\n    {color('green')}👋 Dadah!{color('reset')}\n")
            break
        else:
            print(f"\n    {color('red')}❌ Salah!{color('reset')}")
            time.sleep(1)

if __name__ == "__main__":
    main()
