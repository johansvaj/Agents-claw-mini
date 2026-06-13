#!/usr/bin/env python3
"""
Nexcorix Claw v24.0 - NanoBot/PicoClaw inspired AI Agent
Full modular, workspace markdown, skill loader, MCP, WebUI, cron, permissions.
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import threading
import shutil
import socket
import platform
import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Any

# ========== AUTO REPAIR STRUCTURE ==========
REPAIR_FLAG = os.path.expanduser("~/.nexcorix_repaired")
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(WORK_DIR, "modules")

def ensure_modules():
    if os.path.exists(REPAIR_FLAG):
        return
    print("🔧 Auto-repair: membuat struktur modules...")
    os.makedirs(MODULES_DIR, exist_ok=True)
    # Bersihkan folder module/module bersarang
    for root, dirs, files in os.walk(MODULES_DIR):
        if "module" in dirs:
            shutil.rmtree(os.path.join(root, "module"), ignore_errors=True)
    # Hapus folder module/ di root jika ada
    shutil.rmtree(os.path.join(WORK_DIR, "module"), ignore_errors=True)
    # Buat __init__.py minimal
    init_path = os.path.join(MODULES_DIR, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("# Nexcorix Claw modules\n")
    with open(REPAIR_FLAG, "w") as f:
        f.write("done")
    print("✅ Auto-repair selesai.\n")

ensure_modules()

# ========== Import modul internal ==========
sys.path.insert(0, WORK_DIR)
try:
    dari modul impor  *
kecuali ImportError sebagai e:
    print ( f"⚠️ Beberapa modul belum tersedia: { e } " )
    print ( "Silakan lengkapi file di folder modul/ terlebih dahulu." )
    sistem keluar ( 1 )

# ========== Warna ==========
C = {
    "r" : "\033[0m" , "b" : "\033[1m" , "d" : "\033[2m" , "R" : "\033[91m" , "G" : "\033[92m" ,
    "Y" : "\033[93m" , "C" : "\033[96m" , "O" : "\033[38;5;208m" , "P" : "\033[38;5;141m" ,
}
def  c ( name ) : return C. get ( name, " )
def  clear ( ) : os. system ( "clear"  if os. name != "nt"  else  "cls" )

# ========== Konfigurasi ==========
CONFIG_FILE = os.path.expanduser ( " ~ / .nexcorix/config.json" )
WORKSPACE_DIR = os.path.expanduser ( " ~ / .nexcorix/workspace" )

def  load_cfg ( ) :
    Jika os.path.exists ( CONFIG_FILE ) :​​​
        mencoba :
            dengan  membuka ( CONFIG_FILE )  sebagai f : kembalikan json.load ( f )
        kecuali : lulus
    kembali  {
        "penyedia" : "openrouter" ,
        "model" : "openai/gpt-3.5-turbo" ,
        "openrouter_key" : " ,
        "openai_key": "",
        "anthropic_key": "",
        "google_key": "",
        "deepseek_key": "",
        "temperature": 0.7,
        "max_tokens": 4096,
        "admin_id": "",
        "channels": {}
    }
def save_cfg(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=2)

# ========== System utils ==========
class SystemExecutor:
    def run(self, cmd, timeout=300):
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"success": proc.returncode==0, "stdout": proc.stdout, "stderr": proc.stderr}
    def run_streaming(self, cmd, timeout=300):
        print(c("Y") + f"[ACTION] ⚡ {cmd}" + c("r"))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        out_lines = []
        for line in proc.stdout:
            print(line, end='')
            out_lines.append(line)
        proc.wait(timeout)
        print(c("G") + "[NOTIF] ✅ Selesai" + c("r"))
        return {"success": proc.returncode==0, "stdout": "".join(out_lines)}

class FileManager:
    def __init__(self): self.cwd = os.path.expanduser("~")
    def create_folder(self, name): os.makedirs(os.path.join(self.cwd, name), exist_ok=True); return True, f"Folder {name} dibuat"
    def create_file(self, name, content): 
        with open(os.path.join(self.cwd, name), 'w') as f: f.write(content)
        return True, f"File {name} dibuat"
    def list_files(self): return "\n".join(os.listdir(self.cwd))

class NetworkScanner:
    def __init__(self): self.exec = SystemExecutor()
    def scan_network(self, target="192.168.1.0/24"):
        return self.exec.run(f"nmap -sn {target} 2>/dev/null || ping -c 2 {target.split('/')[0]}")['stdout']

# ========== AI Chat Engine (integrasi modular) ==========
class AIChatEngine:
    def __init__(self):
        self.cfg = load_cfg()
        self.exec = SystemExecutor()
        self.fm = FileManager()
        self.net = NetworkScanner()
        self.llm = LLMProvider(self.cfg)
        self.memory = AdvancedMemory()      # dari modules.advanced_memory
        self.workspace = WorkspaceV2(WORKSPACE_DIR)  # dari modules.workspace_v2
        self.skills = SkillLoader()         # dari modules.skill_loader
        self.mcp = MCPClientV2()            # dari modules.mcp_client_v2
        self.webui = WebUIServer(agent_engine=self, port=18888)
        self.cron = CronService()
        self.perms = PermissionManager()
        self.bus = MessageBus()
        self.agent = AgentLoop(self.bus, self.llm, self.tools, self.memory, self.workspace, self.skills)
        self.conv_history = self.cfg.get("chat_history", {})

    def start_background_services(self):
        self.webui.start_background()
        self.cron.start()
        asyncio.create_task(self.agent.run())

    def test_connection(self):
        return self.llm.test_connection()

    def _casual_response(self, text):
        lower = text.lower().strip()
        if re.search(r'\b(hi|hai|halo|hello)\b', lower):
            return "Halo! Langsung aja perintahnya. 😎"
        if re.search(r'\b(apa kabar|how are you)\b', lower):
            return "Baik! Siap action. 🦂"
        if re.search(r'\b(nama mu|siapa kamu)\b', lower):
            return "Aku Nexcorix Claw, ethical hacker. Panggil Claw aja. 🤘"
        if re.search(r'\b(bisa apa|fitur)\b', lower):
            return (
                "Aku bisa:\n"
                "- install <paket>\n- scan network\n- buat folder <nama>\n- create file <nama> isi <teks>\n- run <perintah>\n- web server\n"
                "Juga punya memori cerdas, skill, MCP, WebUI, dan 25 channel.\n"
                "Atur API key di menu 18 ya!"
            )
        return None

    def process(self, user_id, text):
        lower = text.lower()
        # Perintah langsung (tanpa AI)
        if re.match(r'^(install|pasang) ', lower):
            pkg = text.split(maxsplit=1)[1]
            res = self.exec.run_streaming(f"apt install -y {pkg} 2>/dev/null || pkg install -y {pkg} || pip install {pkg}")
            return f"Instalasi {pkg}: {'OK' if res['success'] else 'Gagal'}\n{res['stdout'][:500]}"
        if re.match(r'scan network', lower):
            target = re.search(r'\d+\.\d+\.\d+\.\d+', text)
            target = target.group() if target else "192.168.1.0/24"
            return self.net.scan_network(target)
        if re.match(r'(create file|buat file) ', lower):
            parts = text.split(maxsplit=2)
            if len(parts) >= 2:
                return self.fm.create_file(parts[1], parts[2] if len(parts)>2 else "")[1]
        if re.match(r'buat folder ', lower):
            name = text.split(maxsplit=1)[1]
            return self.fm.create_folder(name)[1]
        if re.match(r'run ', lower):
            cmd = text[4:]
            return self.exec.run_streaming(cmd)['stdout']
        if re.match(r'web server', lower):
            ip = socket.gethostbyname(socket.gethostname())
            threading.Thread(target=lambda: subprocess.run(["python3", "-m", "http.server", "8080"]), daemon=True).start()
            return f"Web server running at http://{ip}:8080"
        # Kasual
        casual = self._casual_response(text)
        if casual:
            return casual
        # Gunakan AI untuk yang kompleks
        response = self.agent.handle_user_message(user_id, text)
        return response if response else "Maaf, AI tidak merespon. Cek API key."

# ========== Menu Functions ==========
# (Sederhana karena sebagian besar logika sudah di modul)
def show_dashboard(ai):
    clear()
    print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
    print(c("C")+"║"+c("b")+c("Y")+" " * 28 + "DASHBOARD" + " " * 28 + c("r")+c("C")+"║"+c("r"))
    print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
    cfg = ai.cfg
    print(f"\n{c('G')}✅ AI Status: {'Active' if cfg.get('openrouter_key') else 'No API Key'}{c('r')}")
    print(f"{c('C')}📡 Provider: {c('Y')}{cfg.get('provider','openrouter')}{c('r')}")
    print(f"{c('C')}🧠 Model: {c('Y')}{cfg.get('model','openai/gpt-3.5-turbo')}{c('r')}")
    print(f"{c('C')}📁 Workspace: {c('Y')}{WORKSPACE_DIR}{c('r')}")
    input("\n"+c("d")+"Tekan Enter..."+c("r"))

def show_settings_menu(ai):
    cfg = ai.cfg
    while True:
        clear()
        print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
        print(c("C")+"║"+c("b")+c("Y")+" " * 27 + "SETTINGS" + " " * 27 + c("r")+c("C")+"║"+c("r"))
        print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
        print("\n[1] Provider\n[2] Model\n[3] Temperature\n[4] API Keys\n[5] Save & Exit")
        ch = input(c("Y")+"Choice: "+c("r")).strip()
        if ch == "1":
            p = input("Provider (openrouter/openai/anthropic/google/deepseek): ").strip()
            if p: cfg["provider"] = p; save_cfg(cfg)
        elif ch == "2":
            m = input("Model ID: ").strip()
            if m: cfg["model"] = m; save_cfg(cfg)
            ok, msg = ai.test_connection()
            print(c("G")+f"✅ {msg}" if ok else c("R")+f"❌ {msg}")
            input()
        elif ch == "3":
            try: cfg["temperature"] = float(input("Temperature (0-2): ")); save_cfg(cfg)
            except: pass
        elif ch == "4":
            print("1. OpenRouter\n2. OpenAI\n3. Anthropic\n4. Google\n5. DeepSeek")
            sub = input("Choice: ").strip()
            key = input("API Key: ").strip()
            if sub == "1": cfg["openrouter_key"] = key
            elif sub == "2": cfg["openai_key"] = key
            elif sub == "3": cfg["anthropic_key"] = key
            elif sub == "4": cfg["google_key"] = key
            elif sub == "5": cfg["deepseek_key"] = key
            save_cfg(cfg)
            ok, msg = ai.test_connection()
            print(c("G")+f"✅ {msg}" if ok else c("R")+f"❌ {msg}")
            input()
        elif ch == "5": break

def show_channels_menu(ai):
    input("Channels: Gunakan menu 8 untuk melihat daftar (placeholder).\nTekan Enter...")

def show_about():
    clear()
    print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
    print(c("C")+"║"+c("b")+c("Y")+" " * 30 + "ABOUT" + " " * 30 + c("r")+c("C")+"║"+c("r"))
    print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
    print(f"""
{c('O')}Nexcorix Claw v24.0 - Arsitektur NanoBot + PicoClaw{c('r')}
{c('G')}Fitur:{c('r')}
  • Workspace markdown (AGENTS.md, SOUL.md, USER.md, MEMORY.md)
  • Advanced memory with vector DB
  • Skill loader dari SKILL.md
  • MCP client (Model Context Protocol)
  • WebUI workbench (FastAPI)
  • Cron & Heartbeat service
  • Permission management
  • Multi-channel (Telegram, Discord, dll)
  • 100+ AI models via OpenRouter
    """)
    input("Tekan Enter...")

def main():
    ai = AIChatEngine()
    ai.start_background_services()
    clear()
    print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
    print(c("C")+"║"+c("b")+c("Y")+" " * 27 + "NEXCORIX CLAW v24.0" + " " * 27 + c("r")+c("C")+"║"+c("r"))
    print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
    print("\n🔍 Testing AI connection...")
    ok, msg = ai.test_connection()
    if ok: print(c("G")+f"✅ {msg}"+c("r"))
    else: print(c("R")+f"❌ {msg}"+c("r"))
    print(c("d")+"\nTekan Enter untuk menu..."+c("r"))
    input()
    while True:
        clear()
        print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
        print(c("C")+"║"+c("O")+" 🦂 "+c("b")+c("Y")+"      N E X C O R I X   C L A W   v24.0     "+c("O")+"🦂 "+c("C")+"║"+c("r"))
        print(c("C")+"╠══════════════════════════════════════════════════════════╣"+c("r"))
        print(c("C")+"║  [1] Dashboard        [11] Workspace                     ║"+c("r"))
        print(c("C")+"║  [2] Chat             [12] API Keys                      ║"+c("r"))
        print(c("C")+"║  [3] Models           [13] Logs                          ║"+c("r"))
        print(c("C")+"║  [4] Agents           [14] Monitoring                    ║"+c("r"))
        print(c("C")+"║  [5] Memory           [15] Security                      ║"+c("r"))
        print(c("C")+"║  [6] Skills           [16] Backup                        ║"+c("r"))
        print(c("C")+"║  [7] Tools            [17] Updates                       ║"+c("r"))
        print(c("C")+"║  [8] Channels         [18] Settings                      ║"+c("r"))
        print(c("C")+"║  [9] WebUI            [19] About                         ║"+c("r"))
        print(c("C")+"║  [10] Automation      [20] Exit                          ║"+c("r"))
        print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
        choice = input(c("Y")+"Select option: "+c("r")).strip()
        if choice == "1": show_dashboard(ai)
        elif choice == "2":
            clear()
            print(c("C")+"Chat mode (ketik 'exit' kembali)"+c("r"))
            while True:
                inp = input(c("M")+"You: "+c("r")).strip()
                if inp.lower() in ("exit","back"): break
                resp = ai.process("local", inp)
                if resp: print(resp)
        elif choice == "3": input("Models: ganti di Settings (18) → 2\nEnter...")
        elif choice == "4": input("Agents: subagent system coming soon.\nEnter...")
        elif choice == "5": input("Memory: bisa lihat di WebUI.\nEnter...")
        elif choice == "6": input("Skills: buat folder di ~/.nexcorix/skills/\nEnter...")
        elif choice == "7": input("Tools: install, scan, buat folder, file, run, web server.\nEnter...")
        elif choice == "8": show_channels_menu(ai)
        elif choice == "9": print("WebUI running at http://localhost:18888\nEnter..."); input()
        elif choice == "10": input("Automation: cron service active.\nEnter...")
        elif choice == "11": input(f"Workspace: {WORKSPACE_DIR}\nEnter...")
        elif choice == "12": show_settings_menu(ai)
        elif choice == "13": input("Logs: coming soon.\nEnter...")
        elif choice == "14": input("Monitoring: coming soon.\nEnter...")
        elif choice == "15": input("Security: permission manager active.\nEnter...")
        elif choice == "16": input("Backup: manual copy workspace.\nEnter...")
        elif choice == "17": input("Updates: auto-repair on startup.\nEnter...")
        elif choice == "18": show_settings_menu(ai)
        elif choice == "19": show_about()
        elif choice == "20": print(c("G")+"Goodbye! 🦂"+c("r")); break
        else: input("Invalid. Enter...")

if __name__ == "__main__":
    utama ( )
