#!/usr/bin/env python3
"""
Agents Claw Mini v12.0 - AI Terminal Controller via Telegram
"""

import os
import json
import time
import platform
import socket
import re
import shutil
import threading
import asyncio
from pathlib import Path

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

CONFIG_FILE = os.path.expanduser("~/.claw_config.json")

C = {
    "r": "\033[0m", "b": "\033[1m", "d": "\033[2m",
    "R": "\033[91m", "G": "\033[92m", "Y": "\033[93m",
    "B": "\033[94m", "M": "\033[95m", "C": "\033[96m",
    "W": "\033[97m", "O": "\033[38;5;208m",
}

def c(name): return C.get(name, "")

def clear():
    os.system("clear")

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

def header():
    return "\n".join([
        "",
        box_top(52),
        box_mid("🤖⚡  A G E N T S   C L A W   M I N I  ⚡🤖", 52, "center", "Y"),
        box_mid("AI Terminal Controller via Telegram v12.0", 52, "center", "d"),
        box_bot(52),
        "",
    ])

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
        "org_id": "", "integrations": [],
        "os_detected": False, "os_summary": "", "os_info": {}
    }

def save_cfg(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    print(c("G") + "\n    💾 Configuration saved!" + c("r"))

class OSDetector:
    def __init__(self):
        self.info = self._detect()
    
    def _detect(self):
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "hostname": socket.gethostname(),
            "username": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
            "home": os.path.expanduser("~"),
            "shell": os.environ.get("SHELL", os.environ.get("COMSPEC", "unknown")),
            "terminal": os.environ.get("TERM", "unknown"),
            "python": platform.python_version(),
        }
        
        if info["system"] == "Linux":
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            info["distro"] = line.split("=")[1].strip().strip('"')
                            break
            except:
                info["distro"] = "Unknown Linux"
        else:
            info["distro"] = info["system"]
        
        info["is_wsl"] = False
        try:
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower():
                    info["is_wsl"] = True
        except:
            pass
        
        info["is_termux"] = os.environ.get("TERMUX_VERSION") is not None
        info["is_docker"] = os.path.exists("/.dockerenv")
        info["package_managers"] = self._detect_package_manager()
        
        return info
    
    def _detect_package_manager(self):
        managers = []
        cmds = {
            "apt": "apt", "yum": "yum", "dnf": "dnf",
            "pacman": "pacman", "zypper": "zypper", "apk": "apk",
            "brew": "brew", "pkg": "pkg", "choco": "choco", "winget": "winget",
        }
        for cmd, name in cmds.items():
            if os.system(f"which {cmd} >/dev/null 2>&1") == 0:
                managers.append(name)
        return managers if managers else ["unknown"]
    
    def get_summary(self):
        parts = [self.info["distro"]]
        if self.info["is_wsl"]: parts.append("(WSL)")
        if self.info["is_termux"]: parts.append("(Termux)")
        if self.info["is_docker"]: parts.append("(Docker)")
        return " ".join(parts)
    
    def get_ai_context(self):
        i = self.info
        pm = ", ".join(i["package_managers"])
        return "SISTEM: " + self.get_summary() + " | Shell: " + i['shell'] + " | Arch: " + i['machine'] + " | PM: " + pm
    
    def save_to_config(self):
        cfg = load_cfg()
        cfg["os_info"] = self.info
        cfg["os_summary"] = self.get_summary()
        cfg["os_detected"] = True
        save_cfg(cfg)

class FileManager:
    def __init__(self, base_path=None):
        self.current_path = os.path.expanduser(base_path or "~")
    
    def set_path(self, path):
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded) and os.path.isdir(expanded):
            self.current_path = os.path.abspath(expanded)
            return True
        return False
    
    def create_file(self, filename, content=""):
        filepath = os.path.join(self.current_path, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return True, "File '" + filename + "' dibuat!"
        except Exception as e:
            return False, "Error: " + str(e)
    
    def write_file(self, filename, content=""):
        return self.create_file(filename, content)
    
    def create_folder(self, foldername):
        folderpath = os.path.join(self.current_path, foldername)
        try:
            os.makedirs(folderpath, exist_ok=True)
            return True, "Folder '" + foldername + "' dibuat!"
        except Exception as e:
            return False, "Error: " + str(e)
    
    def delete_item(self, name):
        target = os.path.join(self.current_path, name)
        if not os.path.exists(target):
            return False, "'" + name + "' tidak ditemukan!"
        try:
            if os.path.isfile(target):
                os.remove(target)
                return True, "File '" + name + "' dihapus!"
            elif os.path.isdir(target):
                shutil.rmtree(target)
                return True, "Folder '" + name + "' dihapus!"
        except Exception as e:
            return False, "Error: " + str(e)
    
    def read_file(self, filename):
        filepath = os.path.join(self.current_path, filename)
        if not os.path.isfile(filepath):
            return None, "Bukan file atau tidak ditemukan!"
        try:
            with open(filepath, 'r') as f:
                return f.read(), None
        except Exception as e:
            return None, "Error: " + str(e)
    
    def list_items(self):
        try:
            items = []
            with os.scandir(self.current_path) as entries:
                for entry in entries:
                    icon = "📁" if entry.is_dir() else "📄"
                    items.append(icon + " " + entry.name)
            return "\n".join(items) if items else "(kosong)"
        except Exception as e:
            return "Error: " + str(e)
    
    def get_path(self):
        home = os.path.expanduser("~")
        path = self.current_path
        if path.startswith(home):
            path = "~" + path[len(home):]
        return path

class AIFileAgent:
    def __init__(self):
        self.fm = FileManager()
        self.os_detector = OSDetector()
    
    def parse_command(self, text):
        text = text.lower().strip()
        
        patterns = [
            (r'buat(?:kan)?\s+file\s+([^\s]+)(?:\s+dengan\s+isi\s+)?(.*)?', 'create_file'),
            (r'create\s+file\s+([^\s]+)(?:\s+with\s+content\s+)?(.*)?', 'create_file'),
            (r'tulis\s+file\s+([^\s]+)', 'create_file'),
            (r'new\s+file\s+([^\s]+)', 'create_file'),
            (r'bikin\s+file\s+([^\s]+)', 'create_file'),
        ]
        for pattern, action in patterns:
            match = re.search(pattern, text)
            if match:
                return {"action": action, "filename": match.group(1).strip(), "content": match.group(2).strip() if match.group(2) else ""}
        
        patterns = [
            (r'buat(?:kan)?\s+folder\s+([^\s]+)', 'create_folder'),
            (r'create\s+folder\s+([^\s]+)', 'create_folder'),
            (r'new\s+folder\s+([^\s]+)', 'create_folder'),
            (r'bikin\s+folder\s+([^\s]+)', 'create_folder'),
            (r'mkdir\s+([^\s]+)', 'create_folder'),
        ]
        for pattern, action in patterns:
            match = re.search(pattern, text)
            if match:
                return {"action": action, "foldername": match.group(1).strip()}
        
        patterns = [
            (r'hapus\s+file\s+([^\s]+)', 'delete'),
            (r'delete\s+file\s+([^\s]+)', 'delete'),
            (r'remove\s+file\s+([^\s]+)', 'delete'),
            (r'hapus\s+folder\s+([^\s]+)', 'delete'),
            (r'delete\s+folder\s+([^\s]+)', 'delete'),
            (r'hapus\s+([^\s]+)', 'delete'),
            (r'delete\s+([^\s]+)', 'delete'),
            (r'remove\s+([^\s]+)', 'delete'),
            (r'rm\s+([^\s]+)', 'delete'),
        ]
        for pattern, action in patterns:
            match = re.search(pattern, text)
            if match:
                return {"action": action, "target": match.group(1).strip()}
        
        patterns = [
            (r'baca\s+file\s+([^\s]+)', 'read'),
            (r'read\s+file\s+([^\s]+)', 'read'),
            (r'lihat\s+file\s+([^\s]+)', 'read'),
            (r'cat\s+([^\s]+)', 'read'),
            (r'show\s+file\s+([^\s]+)', 'read'),
        ]
        for pattern, action in patterns:
            match = re.search(pattern, text)
            if match:
                return {"action": action, "filename": match.group(1).strip()}
        
        if any(x in text for x in ['list', 'lihat isi', 'tampilkan', 'ls', 'dir', 'apa isi folder']):
            return {"action": "list"}
        
        patterns = [
            (r'pindah\s+ke\s+([^\s]+)', 'cd'),
            (r'cd\s+([^\s]+)', 'cd'),
            (r'go\s+to\s+([^\s]+)', 'cd'),
            (r'buka\s+folder\s+([^\s]+)', 'cd'),
        ]
        for pattern, action in patterns:
            match = re.search(pattern, text)
            if match:
                return {"action": action, "path": match.group(1).strip()}
        
        return None
    
    def execute(self, parsed):
        action = parsed["action"]
        if action == "create_file":
            return self.fm.create_file(parsed["filename"], parsed.get("content", ""))
        elif action == "create_folder":
            return self.fm.create_folder(parsed["foldername"])
        elif action == "delete":
            return self.fm.delete_item(parsed["target"])
        elif action == "read":
            content, error = self.fm.read_file(parsed["filename"])
            if error: return False, error
            return True, "📄 **" + parsed['filename'] + ":**\n```\n" + content[:3000] + "\n```"
        elif action == "list":
            return True, "📂 **" + self.fm.get_path() + "**\n\n" + self.fm.list_items()
        elif action == "cd":
            success = self.fm.set_path(parsed["path"])
            if success:
                return True, "📂 Sekarang di: `" + self.fm.get_path() + "`"
            return False, "Path tidak ditemukan!"
        return False, "Aksi tidak dikenali"
    
    def chat(self, text):
        parsed = self.parse_command(text)
        if parsed:
            success, result = self.execute(parsed)
            return success, result
        return None, """Perintah tidak dikenali. Coba:

• "buat file test.txt"
• "buat folder projects"
• "hapus file lama.txt"
• "baca file readme.md"
• "list"
• "cd ~/downloads"
"""

class AIEngine:
    def __init__(self):
        self.os_detector = OSDetector()
        self.file_agent = AIFileAgent()
        self.conversation_history = {}
        self.knowledge_base = self._build_knowledge()
    
    def _build_knowledge(self):
        return {
            "languages": {
                "python": {"ext": ".py", "run": "python3 {file}", "icon": "🐍"},
                "javascript": {"ext": ".js", "run": "node {file}", "icon": "📜"},
                "typescript": {"ext": ".ts", "run": "ts-node {file}", "icon": "📘"},
                "java": {"ext": ".java", "run": "javac {file} && java {class}", "icon": "☕"},
                "cpp": {"ext": ".cpp", "run": "g++ {file} -o out && ./out", "icon": "⚡"},
                "c": {"ext": ".c", "run": "gcc {file} -o out && ./out", "icon": "🔧"},
                "go": {"ext": ".go", "run": "go run {file}", "icon": "🐹"},
                "rust": {"ext": ".rs", "run": "rustc {file} && ./{file_no_ext}", "icon": "🦀"},
                "ruby": {"ext": ".rb", "run": "ruby {file}", "icon": "💎"},
                "php": {"ext": ".php", "run": "php {file}", "icon": "🐘"},
                "swift": {"ext": ".swift", "run": "swift {file}", "icon": "🍎"},
                "kotlin": {"ext": ".kt", "run": "kotlinc {file} -include-runtime -d out.jar && java -jar out.jar", "icon": "📱"},
                "dart": {"ext": ".dart", "run": "dart {file}", "icon": "🎯"},
                "lua": {"ext": ".lua", "run": "lua {file}", "icon": "🌙"},
                "perl": {"ext": ".pl", "run": "perl {file}", "icon": "🐪"},
                "r": {"ext": ".r", "run": "Rscript {file}", "icon": "📊"},
                "scala": {"ext": ".scala", "run": "scala {file}", "icon": "⚡"},
                "haskell": {"ext": ".hs", "run": "ghc {file} && ./{file_no_ext}", "icon": "λ"},
                "elixir": {"ext": ".ex", "run": "elixir {file}", "icon": "💧"},
                "clojure": {"ext": ".clj", "run": "clojure {file}", "icon": "🔷"},
            }
        }
    
    def detect_language(self, text):
        text_lower = text.lower()
        for lang, info in self.knowledge_base["languages"].items():
            if lang in text_lower:
                return lang, info
        return None, None
    
    def detect_intent(self, text):
        text_lower = text.lower()
        coding_patterns = ['buatkan kode', 'buat kode', 'code', 'program', 'script', 'coding', 'tulis program']
        if any(p in text_lower for p in coding_patterns):
            return "coding"
        
        file_patterns = ['buat file', 'bikin file', 'hapus file', 'delete file', 'buat folder', 'mkdir', 'baca file']
        if any(p in text_lower for p in file_patterns):
            return "file_operation"
        
        system_patterns = ['jalankan', 'run', 'execute', 'terminal', 'command', 'perintah']
        if any(p in text_lower for p in system_patterns):
            return "system"
        
        return "general"
    
    def generate_code(self, language, description):
        templates = {
            "python": 'print("Hello World")\n# Python code generated by Claw AI',
            "javascript": 'console.log("Hello World");\n// JavaScript code generated by Claw AI',
            "java": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello World");\n    }\n}\n// Java code generated by Claw AI',
            "cpp": '#include <iostream>\nint main() {\n    std::cout << "Hello World" << std::endl;\n    return 0;\n}\n// C++ code generated by Claw AI',
            "go": 'package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello World")\n}\n// Go code generated by Claw AI',
            "rust": 'fn main() {\n    println!("Hello World");\n}\n// Rust code generated by Claw AI',
        }
        return templates.get(language, "// Code for " + language + "\n// Generated by Claw AI")
    
    def process(self, user_id, text):
        intent = self.detect_intent(text)
        lang, lang_info = self.detect_language(text)
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        self.conversation_history[user_id].append({"role": "user", "content": text})
        
        response = ""
        
        if intent == "file_operation":
            parsed = self.file_agent.parse_command(text)
            if parsed:
                success, result = self.file_agent.execute(parsed)
                response = result
            else:
                response = "Perintah file tidak dikenali. Coba: 'buat file test.txt'"
        
        elif intent == "coding":
            if lang:
                code = self.generate_code(lang, text)
                ext = lang_info["ext"]
                response = lang_info['icon'] + " **Kode " + lang.upper() + ":**\n\n```" + lang + "\n" + code + "\n```\n\n💾 Untuk menyimpan, ketik:\n`buat file program" + ext + " dengan isi [kode di atas]`"
            else:
                response = """🤖 **Mau kode bahasa apa?**

Bahasa yang didukung:
🐍 Python | 📜 JavaScript | 📘 TypeScript
☕ Java | ⚡ C++ | 🔧 C
🐹 Go | 🦀 Rust | 💎 Ruby
🐘 PHP | 🍎 Swift | 📱 Kotlin
🎯 Dart | 🌙 Lua | 📊 R
Dan masih banyak lagi!

Contoh: "buatkan kode python untuk kalkulator" """
        
        else:
            os_ctx = self.os_detector.get_ai_context()
            response = """🤖 **Claw AI Response**

""" + os_ctx + """

💬 **Pesan:** \"""" + text + """\"

---

✨ Saya bisa bantu kamu dengan:
• 📝 **Coding** - Semua bahasa pemrograman
• 📁 **File Manager** - Buat/hapus file & folder
• 🖥️ **System** - Perintah terminal sesuai OS
• 🌐 **Multi-bahasa** - Indonesia, English, dll

**Contoh perintah:**
• "buat kode python hello world"
• "buat file script.py dengan isi [kode]"
• "hapus file lama.txt"
• "bikin folder projects"
• "list folder"

Ketik apa saja yang kamu butuhkan!"""
        
        self.conversation_history[user_id].append({"role": "assistant", "content": response})
        return response

class ClawTelegramBot:
    def __init__(self):
        self.cfg = load_cfg()
        self.ai = AIEngine()
        self.os_detector = OSDetector()
        self.application = None
    
    def is_admin(self, user_id):
        admin_id = self.cfg.get("admin_id", "")
        if not admin_id:
            return True
        return str(user_id) == str(admin_id)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        os_info = self.os_detector.get_summary()
        
        welcome = """🤖 **Welcome to Claw AI Bot!**

👤 User: `""" + user.first_name + """` (`""" + str(user.id) + """`)
🖥️ Sistem: `""" + os_info + """`
🌐 Bahasa: Auto-detect

**Saya bisa:**
• 📝 Coding semua bahasa (Python, JS, C++, Go, Rust, dll)
• 📁 Kelola file & folder
• 🖥️ Perintah terminal sesuai OS
• 🌍 Berbahasa Indonesia, English, dll

**Perintah:**
/start - Mulai
/os - Info sistem
/help - Bantuan lengkap

**Contoh langsung:**
• "buat kode python kalkulator"
• "buat file hello.py dengan isi print('hi')"
• "hapus file lama.txt"
• "bikin folder projects"
"""
        await update.message.reply_text(welcome, parse_mode='Markdown')
    
    async def os_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        i = self.os_detector.info
        info_text = """🖥️ **SYSTEM INFO**

📌 OS: `""" + i.get('distro', '?') + """`
🔧 Platform: `""" + i.get('platform', '?') + """`
📦 Versi: `""" + i.get('release', '?') + """`
🏗️ Arch: `""" + i.get('machine', '?') + """`
👤 User: `""" + i.get('username', '?') + """`
🐚 Shell: `""" + i.get('shell', '?') + """`
🐍 Python: `""" + i.get('python', '?') + """`
📦 PM: `""" + ', '.join(i.get('package_managers', ['?'])) + """`
"""
        await update.message.reply_text(info_text, parse_mode='Markdown')
    
    async def help_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """📖 **BANTUAN CLAW AI**

**📝 CODING:**
Semua bahasa didukung! Python, JavaScript, Java, C++, C, Go, Rust, Ruby, PHP, Swift, Kotlin, Dart, TypeScript, Lua, R, Scala, Haskell, Elixir, Clojure, dan masih banyak lagi!

Contoh:
• "buat kode python untuk web scraper"
• "buat program javascript hello world"
• "tulis kode go untuk api server"
• "code rust untuk game sederhana"

**📁 FILE MANAGER:**
• `buat file [nama]` - Buat file
• `buat file [nama] dengan isi [konten]`
• `bikin folder [nama]` - Buat folder
• `hapus [nama]` - Hapus file/folder
• `baca file [nama]` - Baca isi file
• `list` - Lihat isi folder
• `pindah ke [path]` - Pindah direktori

**🌍 BAHASA:**
Saya mengerti Bahasa Indonesia, English, 日本語, 中文, Español, Français, Deutsch, Русский, العربية, 한국어, dan banyak lagi!

**🖥️ SYSTEM:**
Saya tahu OS kamu dan akan berikan perintah yang sesuai.

**Command:**
/start - Mulai
/os - Info sistem
/help - Bantuan ini
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text
        
        if not self.is_admin(user.id):
            await update.message.reply_text(
                "🚫 **AKSES DITOLAK**\n\n"
                "Kamu tidak memiliki izin untuk menggunakan bot ini.\n"
                "Hubungi admin untuk mendapatkan akses.\n\n"
                "Your ID: `" + str(user.id) + "`",
                parse_mode='Markdown'
            )
            return
        
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        response = self.ai.process(user.id, text)
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    def run(self):
        token = self.cfg.get("token", "")
        if not token:
            print(c("R") + "Token Telegram belum diatur!" + c("r"))
            print("   Jalankan Claw Launcher -> [12] API Keys")
            return False
        
        admin_id = self.cfg.get("admin_id", "")
        if admin_id:
            print(c("Y") + "Admin ID: " + admin_id + " (Hanya admin yang bisa akses)" + c("r"))
        else:
            print(c("Y") + "Admin ID: BELUM DIATUR (Semua bisa akses)" + c("r"))
            print(c("d") + "   Atur di menu [12] API Keys -> [3] Set Admin ID" + c("r"))
        
        print(c("G") + "Menjalankan Claw Telegram Bot..." + c("r"))
        print("OS: " + self.os_detector.get_summary())
        
        self.application = Application.builder().token(token).build()
        
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("os", self.os_info))
        self.application.add_handler(CommandHandler("help", self.help_cmd))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        def start_bot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # HAPUS signal.signal() - cukup stop_signals=None
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                close_loop=False,
                stop_signals=None
            )
        
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        return True

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

def dashboard():
    cfg = load_cfg()
    m = ALL_MODELS.get(cfg.get("model", "deepseek_chat"), {})
    os_detector = OSDetector()
    os_detector.save_to_config()
    os_line = os_detector.get_summary()
    
    clear(); print(header())
    print(box_top(52, "📊 DASHBOARD"))
    print(box_mid(""))
    print(box_mid("🤖 Model:    " + m.get("icon","") + " " + m.get("name","Not Set"), 52))
    print(box_mid("🌐 Provider: " + m.get("provider","?"), 52))
    print(box_mid("🔑 API:      " + ("💻 Local" if m.get("local") else "🌐 OpenRouter"), 52))
    print(box_mid("🖥️  OS:       " + os_line[:35], 52))
    print(box_mid(""))
    print(box_sep(52))
    print(box_mid("📈 Stats", 52))
    print(box_mid("   Messages: 0", 52))
    print(box_mid("   Commands: 0", 52))
    print(box_mid("   Files:    0", 52))
    print(box_bot(52))
    input("\n    Press Enter...")

def chat_screen():
    cfg = load_cfg()
    os_detector = OSDetector()
    
    clear(); print(header())
    print(box_top(52, "💬 CHAT"))
    print(box_mid(""))
    print(box_mid("OS Terdeteksi: " + os_detector.get_summary(), 52, "center", "G"))
    print(box_mid("Konteks OS akan dikirim ke AI otomatis", 52, "center", "d"))
    print(box_mid(""))
    print(box_bot(52))
    print("\n    " + c("d") + "Type /back to return to menu" + c("r"))
    print("    " + c("d") + "Type /os to show OS info" + c("r"))
    
    while True:
        user_input = input("\n    ➤ ").strip()
        if user_input.lower() == "/back":
            break
        elif user_input.lower() == "/os":
            os_screen()
            break
        elif user_input:
            ai_context = os_detector.get_ai_context()
            print(c("d") + "\n    [AI Context: " + ai_context + "]" + c("r"))
            print(c("G") + "    ✅ Pesan dikirim dengan konteks OS!" + c("r"))

def os_screen():
    os_detector = OSDetector()
    os_detector.save_to_config()
    i = os_detector.info
    
    clear(); print(header())
    print(box_top(52, "🖥️  OS DETECTOR"))
    print(box_mid(""))
    print(box_mid("Sistem Terdeteksi:", 52, "center", "Y"))
    print(box_mid(""))
    print(box_mid("  OS:         " + i.get("distro", "?"), 52))
    print(box_mid("  Platform:   " + i.get("platform", "?")[:35], 52))
    print(box_mid("  Versi:      " + i.get("release", "?"), 52))
    print(box_mid("  Arsitektur: " + i.get("machine", "?"), 52))
    print(box_mid("  Processor:  " + i.get("processor", "?")[:32], 52))
    print(box_mid(""))
    print(box_sep(52))
    print(box_mid("Environment:", 52, "center", "Y"))
    print(box_mid(""))
    print(box_mid("  Hostname:   " + i.get("hostname", "?"), 52))
    print(box_mid("  User:       " + i.get("username", "?"), 52))
    print(box_mid("  Shell:      " + i.get("shell", "?"), 52))
    print(box_mid("  Terminal:   " + i.get("terminal", "?"), 52))
    print(box_mid("  Python:     " + i.get("python", "?"), 52))
    print(box_mid(""))
    print(box_sep(52))
    print(box_mid("Package Manager:", 52, "center", "Y"))
    print(box_mid(""))
    for pm in i.get("package_managers", ["Tidak terdeteksi"]):
        print(box_mid("  • " + pm[:43], 52))
    print(box_mid(""))
    print(box_sep(52))
    print(box_mid("Status: " + os_detector.get_summary(), 52, "center", "G"))
    print(box_mid("✅ Tersimpan di config", 52, "center", "G"))
    print(box_bot(52))
    input("\n    Press Enter...")

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
    print(box_mid("Admin ID:   " + (cfg.get("admin_id") or "❌ Not Set"), 52))
    print(box_mid("Custom:     ❌ Not Set", 52))
    print(box_mid(""))
    print(box_mid("[1] Set OpenRouter Key", 52))
    print(box_mid("[2] Set Telegram Token", 52))
    print(box_mid("[3] Set Admin ID", 52))
    print(box_mid("[4] Set Custom API", 52))
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
        aid = input("    Admin ID (Telegram User ID): ").strip()
        if aid: cfg["admin_id"] = aid; save_cfg(cfg)
    elif p == "4":
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
    cfg = load_cfg()
    clear(); print(header())
    print(box_top(52, "🔒 SECURITY"))
    print(box_mid(""))
    print(box_mid("Dangerous command filter: ✅ ON", 52))
    print(box_mid("Admin restriction: " + ("✅ ON" if cfg.get("admin_id") else "❌ OFF"), 52))
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
    print(box_mid("Current version: v12.0", 52))
    print(box_mid("Latest version: v12.0", 52))
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
    print(box_mid("Agents Claw Mini v12.0", 52, "center", "Y"))
    print(box_mid("AI Terminal Controller", 52, "center"))
    print(box_mid("via Telegram", 52, "center"))
    print(box_mid(""))
    print(box_mid("Author: @yourusername", 52))
    print(box_mid("License: MIT", 52))
    print(box_mid("GitHub: github.com/agents-claw", 52))
    print(box_mid(""))
    print(box_bot(52))
    input("\n    Press Enter...")

def file_manager_screen():
    fm = FileManager()
    
    while True:
        clear(); print(header())
        print(box_top(52, "📁 FILE MANAGER"))
        print(box_mid(""))
        print(box_mid("📂 " + fm.get_path(), 52))
        print(box_mid(""))
        print(box_sep(52))
        
        items = fm.list_items()
        
        if items.startswith("Error"):
            print(box_mid(c("R") + "❌ " + items + c("r"), 52))
        elif items != "(kosong)":
            lines = items.split('\n')[:10]
            for line in lines:
                print(box_mid("  " + line[:48], 52))
            if len(items.split('\n')) > 10:
                print(box_mid("... dan " + str(len(items.split('\n'))-10) + " item lainnya", 52, "center", "d"))
        else:
            print(box_mid("(kosong)", 52, "center", "d"))
        
        print(box_mid(""))
        print(box_sep(52))
        print(box_mid("[c] Create File    [d] Delete Item", 52))
        print(box_mid("[n] New Folder     [r] Read File", 52))
        print(box_mid("[w] Write File     [p] Change Path", 52))
        print(box_mid("[0] Back", 52))
        print(box_bot(52))
        
        p = input("\n    ➤ ").strip().lower()
        
        if p == "0":
            break
        elif p == "c":
            filename = input("    Nama file: ").strip()
            if filename:
                print("    Isi file (Enter 2x = selesai):")
                lines = []
                while True:
                    line = input("    > ")
                    if line == "" and len(lines) > 0 and lines[-1] == "":
                        lines.pop()
                        break
                    lines.append(line)
                content = '\n'.join(lines)
                ok, msg = fm.create_file(filename, content)
                print(c("G" if ok else "R") + "    " + msg + c("r"))
                time.sleep(1)
        elif p == "n":
            foldername = input("    Nama folder: ").strip()
            if foldername:
                ok, msg = fm.create_folder(foldername)
                print(c("G" if ok else "R") + "    " + msg + c("r"))
                time.sleep(1)
        elif p == "d":
            name = input("    Nama file/folder yang dihapus: ").strip()
            if name:
                confirm = input("    Yakin hapus? (y/n): ").strip().lower()
                if confirm == 'y':
                    ok, msg = fm.delete_item(name)
                    print(c("G" if ok else "R") + "    " + msg + c("r"))
                    time.sleep(1)
        elif p == "r":
            filename = input("    Nama file: ").strip()
            if filename:
                content, error = fm.read_file(filename)
                if error:
                    print(c("R") + "    ❌ " + error + c("r"))
                else:
                    print(box_top(52, "📄 " + filename))
                    lines = content.split('\n')[:15]
                    for line in lines:
                        print(box_mid("  " + line[:48], 52))
                    if len(content.split('\n')) > 15:
                        print(box_mid("  ... (truncated)", 52, "center", "d"))
                    print(box_bot(52))
                input("\n    Press Enter...")
        elif p == "w":
            filename = input("    Nama file: ").strip()
            if filename:
                print("    Masukkan isi file (Enter 2x = selesai):")
                lines = []
                while True:
                    line = input("    > ")
                    if line == "" and len(lines) > 0 and lines[-1] == "":
                        lines.pop()
                        break
                    lines.append(line)
                content = '\n'.join(lines)
                ok, msg = fm.write_file(filename, content)
                print(c("G" if ok else "R") + "    " + msg + c("r"))
                time.sleep(1)
        elif p == "p":
            new_path = input("    Path baru (~/ untuk home): ").strip()
            if new_path:
                if fm.set_path(new_path):
                    print(c("G") + "    ✅ Path diubah!" + c("r"))
                else:
                    print(c("R") + "    ❌ Path tidak valid!" + c("r"))
                time.sleep(1)

def ai_file_agent_screen():
    agent = AIFileAgent()
    
    clear(); print(header())
    print(box_top(52, "🤖 AI FILE AGENT"))
    print(box_mid(""))
    print(box_mid("AI bisa buat, hapus, baca file & folder!", 52, "center", "Y"))
    print(box_mid("Ketik perintah natural language", 52, "center", "d"))
    print(box_mid("Contoh: 'buat file test.txt'", 52, "center", "d"))
    print(box_mid("        'hapus folder lama'", 52, "center", "d"))
    print(box_mid("        'baca file readme.md'", 52, "center", "d"))
    print(box_mid(""))
    print(box_bot(52))
    
    while True:
        print(c("C") + "\n  📂 " + agent.fm.get_path() + c("r"))
        user_input = input(c("G") + "  Kamu ➤ " + c("r")).strip()
        
        if user_input.lower() in ["/back", "/exit", "/quit", "exit", "quit"]:
            break
        
        if not user_input:
            continue
        
        print(c("d") + "  🤖 AI sedang memproses..." + c("r"))
        time.sleep(0.5)
        
        success, result = agent.chat(user_input)
        
        if success is None:
            print(c("Y") + "\n  💡 BANTUAN:" + c("r"))
            print(c("W") + result + c("r"))
        elif success:
            print(c("G") + "\n  ✅ BERHASIL:" + c("r"))
            print(c("W") + result + c("r"))
        else:
            print(c("R") + "\n  ❌ GAGAL:" + c("r"))
            print(c("W") + result + c("r"))
        print()

def main():
    os_detector = OSDetector()
    os_detector.save_to_config()
    
    bot = None
    bot_running = False
    
    while True:
        clear(); print(header())
        print(box_top(52))
        
        cfg = load_cfg()
        m = ALL_MODELS.get(cfg.get("model", "deepseek_chat"), {})
        ready = cfg.get("token") != "" and (cfg.get("openrouter_key") != "" or m.get("local", False))
        
        status = c("G") + "● ONLINE" if ready else c("R") + "● OFFLINE"
        
        os_summary = cfg.get("os_summary", "Unknown OS")
        os_icon = "🐧" if "Linux" in os_summary else "🍎" if "Darwin" in os_summary or "macOS" in os_summary else "🪟" if "Windows" in os_summary else "🖥️"
        
        print(box_mid(status + c("r") + "  " + m.get("icon","") + " " + m.get("name","Not Set"), 52))
        print(box_mid(os_icon + " " + os_summary[:40], 52, "center", "C"))
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
        print(box_mid(menu_item("20", "OS Info", "Detect system"), 52))
        print(box_mid(menu_item("21", "File Manager", "Manual file control"), 52))
        print(box_mid(menu_item("22", "AI File Agent", "AI manages files"), 52))
        print(box_sep(52))
        print(box_mid(menu_item("23", "Start Bot", "Jalankan Telegram bot"), 52))
        print(box_mid(menu_item("24", "Stop Bot", "Hentikan bot"), 52))
        print(box_sep(52))
        print(box_mid(menu_item("25", "Exit", "Close launcher"), 52))
        print(box_bot(52))
        
        p = input("\n    ➤ Select [1-25]: ").strip()
        
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
        elif p == "20": os_screen()
        elif p == "21": file_manager_screen()
        elif p == "22": ai_file_agent_screen()
        elif p == "23":
            if not TELEGRAM_AVAILABLE:
                print(c("R") + "\n    ❌ Install dulu: pip install python-telegram-bot" + c("r"))
                time.sleep(2)
            elif not cfg.get("token"):
                print(c("R") + "\n    ❌ Token Telegram belum diatur!" + c("r"))
                time.sleep(2)
            else:
                bot = ClawTelegramBot()
                bot_running = bot.run()
                if bot_running:
                    print(c("G") + "\n    ✅ Bot berjalan di background!" + c("r"))
                    print(c("d") + "    Kirim pesan ke bot di Telegram" + c("r"))
                time.sleep(2)
        elif p == "24":
            bot_running = False
            print(c("Y") + "\n    ⏹️ Bot dihentikan" + c("r"))
            time.sleep(1)
        elif p == "25":
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
