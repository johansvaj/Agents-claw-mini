#!/usr/bin/env python3
"""
🤖⚡ Agents Claw Mini v11.3 - AI Terminal Controller via Telegram
+ OS Detector + File Manager + AI File Agent
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
import platform
import socket
import shutil
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
        box_mid("AI Terminal Controller via Telegram v11.3", 52, "center", "d"),
        box_bot(52),
        "",
    ])

# ── OS DETECTOR ──
class OSDetector:
    """Deteksi OS untuk terminal"""
    
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
            "apt": "apt (Debian/Ubuntu)",
            "yum": "yum (RHEL)",
            "dnf": "dnf (Fedora)",
            "pacman": "pacman (Arch)",
            "zypper": "zypper (openSUSE)",
            "apk": "apk (Alpine)",
            "brew": "brew (macOS)",
            "pkg": "pkg (Termux)",
            "choco": "choco (Windows)",
            "winget": "winget (Windows)",
        }
        for cmd, name in cmds.items():
            if os.system(f"which {cmd} >/dev/null 2>&1") == 0:
                managers.append(name)
        return managers if managers else ["Tidak terdeteksi"]
    
    def get_summary(self):
        parts = [self.info["distro"]]
        if self.info["is_wsl"]:
            parts.append("(WSL)")
        if self.info["is_termux"]:
            parts.append("(Termux)")
        if self.info["is_docker"]:
            parts.append("(Docker)")
        return " ".join(parts)
    
    def get_os_line(self):
        return self.get_summary()
    
    def save_to_config(self):
        cfg = load_cfg()
        cfg["os_info"] = self.info
        cfg["os_summary"] = self.get_summary()
        cfg["os_detected"] = True
        save_cfg(cfg)
    
    def get_ai_context(self):
        i = self.info
        pm = ", ".join(i["package_managers"])
        return f"""[SYSTEM: {self.get_summary()} | Shell: {i['shell']} | PM: {pm}]"""

def get_os_detector():
    return OSDetector()

# ── FILE MANAGER ──
class FileManager:
    """Manajemen file dan folder"""
    
    def __init__(self, base_path=None):
        self.base_path = base_path or os.getcwd()
        self.current_path = os.path.expanduser(self.base_path)
    
    def set_path(self, path):
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded) and os.path.isdir(expanded):
            self.current_path = os.path.abspath(expanded)
            return True
        return False
    
    def list_items(self, path=None):
        target = path or self.current_path
        target = os.path.expanduser(target)
        
        if not os.path.exists(target):
            return None, "Path tidak ditemukan!"
        
        try:
            items = []
            with os.scandir(target) as entries:
                for entry in entries:
                    item_type = "📁" if entry.is_dir() else "📄"
                    size = ""
                    if entry.is_file():
                        try:
                            sz = entry.stat().st_size
                            if sz < 1024:
                                size = f"{sz}B"
                            elif sz < 1024*1024:
                                size = f"{sz/1024:.1f}KB"
                            else:
                                size = f"{sz/(1024*1024):.1f}MB"
                        except:
                            size = "?"
                    items.append({
                        "name": entry.name,
                        "type": "folder" if entry.is_dir() else "file",
                        "icon": item_type,
                        "size": size,
                        "path": entry.path
                    })
            
            items.sort(key=lambda x: (0 if x["type"] == "folder" else 1, x["name"].lower()))
            return items, None
            
        except PermissionError:
            return None, "Akses ditolak!"
        except Exception as e:
            return None, str(e)
    
    def create_file(self, filename, content=""):
        filepath = os.path.join(self.current_path, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return True, f"File '{filename}' berhasil dibuat!"
        except Exception as e:
            return False, str(e)
    
    def create_folder(self, foldername):
        folderpath = os.path.join(self.current_path, foldername)
        try:
            os.makedirs(folderpath, exist_ok=True)
            return True, f"Folder '{foldername}' berhasil dibuat!"
        except Exception as e:
            return False, str(e)
    
    def delete_item(self, name):
        target = os.path.join(self.current_path, name)
        
        if not os.path.exists(target):
            return False, f"'{name}' tidak ditemukan!"
        
        try:
            if os.path.isfile(target):
                os.remove(target)
                return True, f"File '{name}' berhasil dihapus!"
            elif os.path.isdir(target):
                shutil.rmtree(target)
                return True, f"Folder '{name}' berhasil dihapus!"
        except Exception as e:
            return False, str(e)
    
    def read_file(self, filename):
        filepath = os.path.join(self.current_path, filename)
        if not os.path.isfile(filepath):
            return None, "Bukan file atau tidak ditemukan!"
        
        try:
            with open(filepath, 'r') as f:
                return f.read(), None
        except Exception as e:
            return None, str(e)
    
    def write_file(self, filename, content):
        filepath = os.path.join(self.current_path, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return True, f"File '{filename}' berhasil diupdate!"
        except Exception as e:
            return False, str(e)
    
    def get_path_display(self):
        home = os.path.expanduser("~")
        path = self.current_path
        if path.startswith(home):
            path = "~" + path[len(home):]
        return path

# ── AI FILE AGENT (NEW) ──
class AIFileAgent:
    """AI Agent untuk mengelola file via perintah natural language"""
    
    def __init__(self):
        self.fm = FileManager()
        self.os_detector = get_os_detector()
    
    def parse_command(self, user_input):
        """Parse perintah natural language ke aksi file"""
        text = user_input.lower().strip()
        
        # ── BUAT FILE ──
        patterns_create_file = [
            r'buat(?:kan)?\s+file\s+([^\s]+)(?:\s+dengan\s+isi\s+)?(.*)?',
            r'create\s+file\s+([^\s]+)(?:\s+with\s+content\s+)?(.*)?',
            r'tulis\s+file\s+([^\s]+)',
            r'new\s+file\s+([^\s]+)',
            r'bikin\s+file\s+([^\s]+)',
        ]
        
        for pattern in patterns_create_file:
            match = re.search(pattern, text)
            if match:
                filename = match.group(1).strip()
                content = match.group(2).strip() if match.group(2) else ""
                return {
                    "action": "create_file",
                    "filename": filename,
                    "content": content
                }
        
        # ── BUAT FOLDER ──
        patterns_create_folder = [
            r'buat(?:kan)?\s+folder\s+([^\s]+)',
            r'create\s+folder\s+([^\s]+)',
            r'new\s+folder\s+([^\s]+)',
            r'bikin\s+folder\s+([^\s]+)',
            r'buat(?:kan)?\s+direktori\s+([^\s]+)',
            r'mkdir\s+([^\s]+)',
        ]
        
        for pattern in patterns_create_folder:
            match = re.search(pattern, text)
            if match:
                return {
                    "action": "create_folder",
                    "foldername": match.group(1).strip()
                }
        
        # ── HAPUS FILE/FOLDER ──
        patterns_delete = [
            r'hapus\s+file\s+([^\s]+)',
            r'delete\s+file\s+([^\s]+)',
            r'remove\s+file\s+([^\s]+)',
            r'hapus\s+folder\s+([^\s]+)',
            r'delete\s+folder\s+([^\s]+)',
            r'remove\s+folder\s+([^\s]+)',
            r'hapus\s+direktori\s+([^\s]+)',
            r'hapus\s+([^\s]+)',
            r'delete\s+([^\s]+)',
            r'remove\s+([^\s]+)',
            r'rm\s+([^\s]+)',
            r'rmdir\s+([^\s]+)',
        ]
        
        for pattern in patterns_delete:
            match = re.search(pattern, text)
            if match:
                target = match.group(1).strip()
                # Deteksi apakah file atau folder
                target_path = os.path.join(self.fm.current_path, target)
                item_type = "folder" if os.path.isdir(target_path) else "file"
                return {
                    "action": "delete",
                    "target": target,
                    "type": item_type
                }
        
        # ── BACA FILE ──
        patterns_read = [
            r'baca\s+file\s+([^\s]+)',
            r'read\s+file\s+([^\s]+)',
            r'lihat\s+file\s+([^\s]+)',
            r'cat\s+([^\s]+)',
            r'show\s+file\s+([^\s]+)',
        ]
        
        for pattern in patterns_read:
            match = re.search(pattern, text)
            if match:
                return {
                    "action": "read",
                    "filename": match.group(1).strip()
                }
        
        # ── LIST/TAMPILKAN ──
        patterns_list = [
            r'list\s+folder',
            r'lihat\s+folder',
            r'tampilkan\s+isi',
            r'show\s+contents',
            r'ls',
            r'dir',
            r'apa\s+isi\s+folder',
        ]
        
        for pattern in patterns_list:
            if re.search(pattern, text):
                return {
                    "action": "list"
                }
        
        # ── PINDAH DIREKTORI ──
        patterns_cd = [
            r'pindah\s+ke\s+([^\s]+)',
            r'cd\s+([^\s]+)',
            r'go\s+to\s+([^\s]+)',
            r'change\s+dir\s+([^\s]+)',
            r'buka\s+folder\s+([^\s]+)',
        ]
        
        for pattern in patterns_cd:
            match = re.search(pattern, text)
            if match:
                return {
                    "action": "change_path",
                    "path": match.group(1).strip()
                }
        
        # ── EDIT/TULIS ULANG ──
        patterns_edit = [
            r'edit\s+file\s+([^\s]+)(?:\s+jadi\s+)?(.*)?',
            r'update\s+file\s+([^\s]+)(?:\s+with\s+)?(.*)?',
            r'ubah\s+file\s+([^\s]+)(?:\s+menjadi\s+)?(.*)?',
        ]
        
        for pattern in patterns_edit:
            match = re.search(pattern, text)
            if match:
                return {
                    "action": "write",
                    "filename": match.group(1).strip(),
                    "content": match.group(2).strip() if match.group(2) else ""
                }
        
        return None
    
    def execute(self, parsed):
        """Eksekusi perintah yang sudah di-parse"""
        action = parsed["action"]
        
        if action == "create_file":
            return self.fm.create_file(parsed["filename"], parsed.get("content", ""))
        
        elif action == "create_folder":
            return self.fm.create_folder(parsed["foldername"])
        
        elif action == "delete":
            return self.fm.delete_item(parsed["target"])
        
        elif action == "read":
            content, error = self.fm.read_file(parsed["filename"])
            if error:
                return False, error
            return True, content
        
        elif action == "list":
            items, error = self.fm.list_items()
            if error:
                return False, error
            result = f"📂 {self.fm.get_path_display()}\n"
            for item in items:
                size_info = f" ({item['size']})" if item['size'] else ""
                result += f"  {item['icon']} {item['name']}{size_info}\n"
            return True, result
        
        elif action == "change_path":
            success = self.fm.set_path(parsed["path"])
            if success:
                return True, f"📂 Sekarang di: {self.fm.get_path_display()}"
            return False, "Path tidak ditemukan!"
        
        elif action == "write":
            return self.fm.write_file(parsed["filename"], parsed.get("content", ""))
        
        return False, "Aksi tidak dikenali"
    
    def chat(self, user_input):
        """Proses input user dan eksekusi"""
        parsed = self.parse_command(user_input)
        
        if not parsed:
            # Bukan perintah file, berikan bantuan
            return None, f"""🤖 Saya tidak mengerti perintah file tersebut.

Perintah yang bisa saya lakukan:
  📄 Buat File    : "buat file test.txt dengan isi halo"
  📁 Buat Folder  : "buat folder projects" / "mkdir myfolder"
  🗑️  Hapus        : "hapus file test.txt" / "delete folder old"
  📖 Baca File     : "baca file test.txt" / "cat readme.md"
  📂 List Isi      : "list folder" / "ls"
  📍 Pindah Path   : "pindah ke ~/Documents" / "cd .."
  ✏️  Edit File     : "edit file test.txt jadi hello world"

Path aktif: {self.fm.get_path_display()}"""
        
        # Eksekusi perintah
        success, result = self.execute(parsed)
        return success, result

def ai_file_agent_screen():
    """Layar AI File Agent - Chat dengan AI untuk kelola file"""
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
        print(c("C") + f"\n  📂 {agent.fm.get_path_display()}" + c("r"))
        user_input = input(c("G") + "  Kamu ➤ " + c("r")).strip()
        
        if user_input.lower() in ["/back", "/exit", "/quit", "exit", "quit"]:
            break
        
        if not user_input:
            continue
        
        print(c("d") + "  🤖 AI sedang memproses..." + c("r"))
        time.sleep(0.5)
        
        success, result = agent.chat(user_input)
        
        if success is None:
            # Bukan perintah file, tampilkan bantuan
            print(c("Y") + "\n  💡 BANTUAN:" + c("r"))
            print(c("W") + result + c("r"))
        elif success:
            print(c("G") + "\n  ✅ BERHASIL:" + c("r"))
            print(c("W") + result + c("r"))
        else:
            print(c("R") + "\n  ❌ GAGAL:" + c("r"))
            print(c("W") + result + c("r"))
        
        print()

def file_manager_screen():
    """Layar File Manager Manual"""
    fm = FileManager()
    
    while True:
        clear(); print(header())
        print(box_top(52, "📁 FILE MANAGER"))
        print(box_mid(""))
        print(box_mid("📂 " + fm.get_path_display(), 52))
        print(box_mid(""))
        print(box_sep(52))
        
        items, error = fm.list_items()
        
        if error:
            print(box_mid(c("R") + "❌ " + error + c("r"), 52))
        elif items:
            for i, item in enumerate(items[:10], 1):
                display = f"{item['icon']} {item['name'][:30]}"
                if item['size']:
                    display += f" ({item['size']})"
                print(box_mid(f"[{i}] {display}", 52))
            
            if len(items) > 10:
                print(box_mid(f"... dan {len(items)-10} item lainnya", 52, "center", "d"))
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
                    print(box_top(52, f"📄 {filename}"))
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
        
        elif p.isdigit() and items:
            idx = int(p) - 1
            if 0 <= idx < len(items):
                item = items[idx]
                if item["type"] == "folder":
                    fm.set_path(item["path"])
                else:
                    print(box_top(52, f"📄 {item['name']}"))
                    content, error = fm.read_file(item["name"])
                    if error:
                        print(box_mid("❌ " + error, 52))
                    else:
                        lines = content.split('\n')[:15]
                        for line in lines:
                            print(box_mid("  " + line[:48], 52))
                        if len(content.split('\n')) > 15:
                            print(box_mid("  ... (truncated)", 52, "center", "d"))
                    print(box_bot(52))
                    input("\n    Press Enter...")

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
        "org_id": "", "integrations": [],
        "os_detected": False, "os_summary": "", "os_info": {}
    }

def save_cfg(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    print(c("G") + "\n    💾 Configuration saved!" + c("r"))

# ── SCREENS ──

def dashboard():
    cfg = load_cfg()
    m = ALL_MODELS.get(cfg.get("model", "deepseek_chat"), {})
    os_detector = get_os_detector()
    os_detector.save_to_config()
    os_line = os_detector.get_os_line()
    
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
    os_detector = get_os_detector()
    
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
    os_detector = get_os_detector()
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
    print(box_mid("Current version: v11.3", 52))
    print(box_mid("Latest version: v11.3", 52))
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
    print(box_mid("Agents Claw Mini v11.3", 52, "center", "Y"))
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
    os_detector = get_os_detector()
    os_detector.save_to_config()
    
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
        print(box_mid(menu_item("23", "Exit", "Close launcher"), 52))
        print(box_bot(52))
        
        p = input("\n    ➤ Select [1-23]: ").strip()
        
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
