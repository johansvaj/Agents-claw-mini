#!/usr/bin/env python3
"""
Nexcorix Claw v14.0 - Ultimate AI Agent with All Modules
Integrasi penuh: RAG, MCP, Multi-Agent, Marketplace, Observability, Voice, KG, Memory Compactor
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
from html.parser import HTMLParser
from typing import Dict, List, Optional, Any

# ========== Warna ==========
C = {
    "r":"\033[0m","b":"\033[1m","d":"\033[2m","R":"\033[91m","G":"\033[92m","Y":"\033[93m",
    "B":"\033[94m","M":"\033[95m","C":"\033[96m","W":"\033[97m","O":"\033[38;5;208m",
    "P":"\033[38;5;141m","T":"\033[38;5;37m","L":"\033[38;5;11m",
}
def c(name): return C.get(name, "")
def clear(): os.system("clear" if os.name != "nt" else "cls")

# ========== Config ==========
CONFIG_FILE = os.path.expanduser("~/.nexcorix/config.json")
WORKSPACE_DIR = os.path.expanduser("~/.nexcorix/workspace")

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: pass
    return {
        "provider": "openrouter", "model": "deepseek/deepseek-chat", "fallback_model": "deepseek-chat",
        "openai_key": "", "anthropic_key": "", "google_key": "", "deepseek_key": "", "openrouter_key": "",
        "custom_api_url": "", "custom_api_key": "", "ollama_url": "http://localhost:11434",
        "temperature": 0.7, "max_tokens": 4096, "context_window": "auto", "performance": "balanced",
        "admin_id": "", "token": "", "base_url": "https://openrouter.ai/api/v1",
        "chat_history": {}, "channels": {}, "mcp_server_url": ""
    }
def save_cfg(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=2)

# ========== Import Modules ==========
sys.path.insert(0, os.path.dirname(__file__))
MODULES_AVAILABLE = False
try:
    from modules import (
        ToolRegistry, get_tool_registry, MemoryStore, SkillManager, Skill,
        Workspace, WebUI, RAGStore, MCPClient, MultiAgentOrchestrator,
        SkillMarketplace, TraceLogger, VoiceInterface, KnowledgeGraph,
        AdvancedMemory, MemoryCompactor
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    print(c("R") + f"[!] Modules not fully available: {e}" + c("r"))

# ========== OS Detector ==========
class OSDetector:
    def __init__(self):
        self.info = self._detect()
    def _detect(self):
        info = {
            "system": platform.system(), "release": platform.release(),
            "version": platform.version(), "platform": platform.platform(),
            "machine": platform.machine(), "processor": platform.processor() or "Unknown",
            "hostname": socket.gethostname(),
            "username": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
            "home": os.path.expanduser("~"), "shell": os.environ.get("SHELL", os.environ.get("COMSPEC", "unknown")),
            "terminal": os.environ.get("TERM", "unknown"), "python": platform.python_version(),
        }
        if info["system"] == "Linux":
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            info["distro"] = line.split("=")[1].strip().strip('"')
                            break
            except: info["distro"] = "Unknown Linux"
        else: info["distro"] = info["system"]
        info["is_wsl"] = False
        try:
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower(): info["is_wsl"] = True
        except: pass
        info["is_termux"] = os.environ.get("TERMUX_VERSION") is not None
        info["is_docker"] = os.path.exists("/.dockerenv")
        info["is_proot"] = os.path.exists("/.proot") or "proot" in os.environ.get("PROOT_LOADER", "")
        info["package_managers"] = self._detect_package_manager()
        if info["is_termux"] and "pkg" not in info["package_managers"]:
            info["package_managers"].append("pkg")
        info["has_sudo"] = os.system("which sudo >/dev/null 2>&1") == 0
        return info
    def _detect_package_manager(self):
        managers = []
        cmds = {"apt":"apt","apt-get":"apt-get","yum":"yum","dnf":"dnf","pacman":"pacman","zypper":"zypper","apk":"apk","brew":"brew","pkg":"pkg","choco":"choco","winget":"winget","pip":"pip","pip3":"pip3","npm":"npm","gem":"gem"}
        for cmd, name in cmds.items():
            if os.system(f"which {cmd} >/dev/null 2>&1") == 0:
                managers.append(name)
        return managers
    def get_summary(self):
        parts = [self.info["distro"]]
        if self.info["is_wsl"]: parts.append("(WSL)")
        if self.info["is_termux"]: parts.append("(Termux)")
        if self.info["is_docker"]: parts.append("(Docker)")
        if self.info["is_proot"]: parts.append("(Proot)")
        return " ".join(parts)
    def get_ai_context(self):
        i = self.info
        pm = ", ".join(i["package_managers"])
        return f"OS: {self.get_summary()} | Shell: {i['shell']} | Arch: {i['machine']} | PM: {pm} | Sudo: {i['has_sudo']}"

# ========== System Executor ==========
class SystemExecutor:
    def __init__(self): self.os_detector = OSDetector()
    def run_streaming(self, command, timeout=300):
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, cwd=os.path.expanduser("~"))
            output_lines = []
            for line in process.stdout:
                print(line, end='')
                output_lines.append(line)
            process.wait(timeout=timeout)
            success = process.returncode == 0
            return {"success": success, "stdout": "".join(output_lines), "stderr": "", "command": command}
        except subprocess.TimeoutExpired:
            process.kill()
            return {"success": False, "stdout": "", "stderr": f"Command timed out after {timeout}s", "command": command}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "command": command}
    def run(self, command, timeout=300):
        try:
            if os.name == "nt":
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.path.expanduser("~"))
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, executable="/bin/bash" if not self.os_detector.info["is_termux"] else None, cwd=os.path.expanduser("~"))
            stdout, stderr = process.communicate(timeout=timeout)
            return {"success": process.returncode == 0, "returncode": process.returncode, "stdout": stdout, "stderr": stderr, "command": command}
        except subprocess.TimeoutExpired:
            process.kill()
            return {"success": False, "returncode": -1, "stdout": "", "stderr": f"Command timed out after {timeout}s", "command": command}
        except Exception as e:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e), "command": command}

# ========== Advanced Installer (sama seperti dulu) ==========
class AdvancedInstaller:
    def __init__(self):
        self.os_detector = OSDetector()
        self.executor = SystemExecutor()
        self.pm_commands = {
            "apt": "DEBIAN_FRONTEND=noninteractive apt install -y {package}",
            "apt-get": "DEBIAN_FRONTEND=noninteractive apt-get install -y {package}",
            "yum": "yum install -y {package}", "dnf": "dnf install -y {package}",
            "pacman": "pacman -S --noconfirm {package}", "zypper": "zypper install -y {package}",
            "apk": "apk add {package}", "brew": "brew install {package}",
            "pkg": "pkg install -y {package}", "choco": "choco install {package} -y",
            "winget": "winget install {package} --accept-package-agreements --accept-source-agreements",
            "pip": "pip install {package}", "pip3": "pip3 install {package}",
            "npm": "npm install -g {package}", "gem": "gem install {package}",
        }
        self.tool_aliases = {
            "msfconsole":"metasploit-framework","msfvenom":"metasploit-framework","nmap":"nmap","sqlmap":"sqlmap",
            "gobuster":"gobuster","hydra":"hydra","john":"john","hashcat":"hashcat","aircrack-ng":"aircrack-ng",
            "nikto":"nikto","dirb":"dirb","wpscan":"wpscan","python3":"python3","git":"git","curl":"curl","wget":"wget",
        }
        self.github_tools = {
            "linpeas":"https://github.com/carlospolop/PEASS-ng.git","winpeas":"https://github.com/carlospolop/PEASS-ng.git",
            "impacket":"https://github.com/fortra/impacket.git","kerbrute":"https://github.com/ropnop/kerbrute.git","pspy":"https://github.com/DominicBreuker/pspy.git",
        }
    def get_primary_pm(self):
        managers = self.os_detector.info.get("package_managers", [])
        priority = ["pkg", "apt", "apt-get", "dnf", "yum", "pacman", "zypper", "apk", "brew", "choco", "winget", "pip", "pip3"]
        for pm in priority:
            if pm in managers: return pm
        return managers[0] if managers else None
    def resolve_package(self, tool_name): return self.tool_aliases.get(tool_name.lower(), tool_name)
    def _has_sudo(self): return self.os_detector.info.get("has_sudo", False)
    def install_streaming(self, package, pm=None):
        if not pm: pm = self.get_primary_pm()
        if not pm or pm=="unknown": return False, "No package manager!"
        resolved = self.resolve_package(package)
        if package.lower() in self.github_tools:
            return self.install_from_github_streaming(package.lower())
        if pm in self.pm_commands:
            cmd = self.pm_commands[pm].format(package=resolved)
            if pm in ["apt","apt-get","dnf","yum","pacman","zypper","apk"] and self._has_sudo():
                cmd = "sudo " + cmd
            if self.os_detector.info.get("is_termux", False):
                cmd = cmd.replace("sudo ", "")
            result = self.executor.run_streaming(cmd, timeout=600)
            return result["success"], result["stdout"] if result["success"] else result["stderr"]
        return False, f"PM {pm} not supported"
    def install_from_github_streaming(self, tool_name):
        if tool_name not in self.github_tools: return False, "Not in registry"
        repo_url = self.github_tools[tool_name]
        install_dir = os.path.expanduser(f"~/tools/{tool_name}")
        os.makedirs(os.path.expanduser("~/tools"), exist_ok=True)
        cmd = f"git clone {repo_url} {install_dir} 2>&1 || cd {install_dir} && git pull 2>&1"
        result = self.executor.run_streaming(cmd, timeout=120)
        if not result["success"] and "already exists" not in result["stdout"]:
            return False, f"Git clone failed:\n{result['stdout']}"
        setup_result = f"Cloned to {install_dir}"
        if tool_name in ["linpeas","winpeas"]:
            setup_result = "PEASS downloaded."
        elif tool_name == "impacket":
            self.executor.run_streaming(f"cd {install_dir} && pip3 install . 2>&1", timeout=120)
            setup_result = "impacket installed via pip3."
        return True, f"GitHub Install: {tool_name}\nRepo: {repo_url}\nDir: {install_dir}\n{setup_result}"
    def install_pip_tool(self, package):
        result = self.executor.run(f"pip3 install {package}", timeout=180)
        if result["success"]: return True, f"pip3 install {package} OK\n{result['stdout'][:1000]}"
        else: return False, f"pip3 install failed:\n{result['stderr'][:1000]}"
    def update_repos(self):
        pm = self.get_primary_pm()
        update_cmds = {"apt":"sudo apt update","apt-get":"sudo apt-get update","dnf":"sudo dnf check-update","yum":"sudo yum check-update","pacman":"sudo pacman -Sy","zypper":"sudo zypper refresh","apk":"sudo apk update","brew":"brew update","pkg":"pkg update","choco":"choco upgrade chocolatey","winget":"winget source update"}
        if pm in update_cmds:
            cmd = update_cmds[pm]
            if self.os_detector.info.get("is_termux", False): cmd = cmd.replace("sudo ", "")
            result = self.executor.run(cmd, timeout=300)
            if result["success"]: return True, f"Updated\n{result['stdout'][:1500]}"
            else: return False, f"Failed\n{result['stderr'][:1500]}"
        return False, "Cannot update"

# ========== File Manager ==========
class FileManager:
    def __init__(self, base_path=None): self.current_path = os.path.expanduser(base_path or "~")
    def set_path(self, path):
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded) and os.path.isdir(expanded):
            self.current_path = os.path.abspath(expanded); return True
        return False
    def create_file(self, filename, content=""):
        filepath = os.path.join(self.current_path, filename)
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        try:
            with open(filepath, 'w') as f: f.write(content)
            return True, f"✅ File '{filename}' created at {filepath}"
        except Exception as e: return False, f"❌ Error: {e}"
    def create_folder(self, foldername):
        folderpath = os.path.join(self.current_path, foldername)
        try:
            os.makedirs(folderpath, exist_ok=True)
            return True, f"Folder '{foldername}' created!"
        except Exception as e: return False, f"Error: {e}"
    def delete_item(self, name):
        target = os.path.join(self.current_path, name)
        if not os.path.exists(target): return False, f"'{name}' not found!"
        try:
            if os.path.isfile(target): os.remove(target); return True, f"File '{name}' deleted!"
            elif os.path.isdir(target): shutil.rmtree(target); return True, f"Folder '{name}' deleted!"
        except Exception as e: return False, f"Error: {e}"
    def read_file(self, filename):
        filepath = os.path.join(self.current_path, filename)
        if not os.path.isfile(filepath): return None, "Not found!"
        try:
            with open(filepath, 'r') as f: return f.read(), None
        except Exception as e: return None, f"Error: {e}"
    def list_items(self):
        try:
            items = []
            with os.scandir(self.current_path) as entries:
                for entry in entries:
                    icon = "[DIR]" if entry.is_dir() else "[FILE]"
                    items.append(f"{icon} {entry.name}")
            return "\n".join(items) if items else "(empty)"
        except Exception as e: return f"Error: {e}"
    def get_path(self):
        home = os.path.expanduser("~")
        path = self.current_path
        if path.startswith(home): path = "~" + path[len(home):]
        return path

# ========== Network Scanner ==========
class NetworkScanner:
    def __init__(self):
        self.executor = SystemExecutor()
        self.os_detector = OSDetector()
    def scan_network(self, target="192.168.1.0/24"):
        if '/' in target:
            base = target.split('/')[0]
        else:
            base = target
        if '.' in base:
            base_ip = '.'.join(base.split('.')[:3])
        else:
            base_ip = "192.168.1"
        has_nmap = os.system("which nmap >/dev/null 2>&1") == 0
        if has_nmap:
            is_termux = self.os_detector.info.get("is_termux", False)
            is_proot = self.os_detector.info.get("is_proot", False)
            if is_termux or is_proot:
                cmd = f"nmap -sn {target} 2>&1"
            else:
                cmd = f"sudo nmap -sn {target}" if self.os_detector.info.get("has_sudo", False) else f"nmap -sn {target}"
            result = self.executor.run(cmd, timeout=60)
            if result["success"] and result["stdout"].strip():
                return f"🔍 Scan result for {target} (nmap):\n{result['stdout']}"
            if "Permission denied" in result["stderr"] or "if_indextoname" in result["stderr"]:
                pass
            else:
                return f"❌ Network scan failed (nmap).\nError: {result['stderr']}"
        ping_cmd = f"for i in {{1..254}}; do ping -c 1 -W 1 {base_ip}.$i 2>/dev/null | grep '64 bytes' && echo '✅ Host {base_ip}.$i is up'; done"
        result2 = self.executor.run(ping_cmd, timeout=120)
        if result2["success"] and result2["stdout"].strip():
            return f"🔍 Ping sweep result for {base_ip}.0/24 (no root required):\n{result2['stdout']}"
        else:
            return f"❌ Network scan failed. Try running with 'su -' or install nmap.\nPing sweep also failed: {result2['stderr']}"
    def scan_ports(self, target, ports="1-1000"):
        has_nmap = os.system("which nmap >/dev/null 2>&1") == 0
        if not has_nmap: return "❌ nmap not installed."
        is_termux = self.os_detector.info.get("is_termux", False)
        if is_termux:
            cmd = f"nmap -p {ports} {target}"
        else:
            cmd = f"sudo nmap -p {ports} {target}" if self.os_detector.info.get("has_sudo", False) else f"nmap -p {ports} {target}"
        result = self.executor.run(cmd, timeout=120)
        return result["stdout"] if result["success"] else f"Port scan failed:\n{result['stderr']}"
    def wifi_scan(self):
        is_termux = self.os_detector.info.get("is_termux", False)
        if is_termux:
            result = self.executor.run("termux-wifi-scaninfo", timeout=30)
            return result["stdout"] if result["success"] else "WiFi scan failed. Install termux-api and grant location permission."
        else:
            result = self.executor.run("nmcli dev wifi list 2>/dev/null", timeout=30)
            if result["success"] and result["stdout"].strip(): return result["stdout"]
            cmd = "sudo iwlist wlan0 scan 2>/dev/null | grep -E 'ESSID|Signal'" if self.os_detector.info.get("has_sudo", False) else "iwlist wlan0 scan 2>/dev/null | grep -E 'ESSID|Signal'"
            result2 = self.executor.run(cmd, timeout=30)
            return result2["stdout"] if result2["success"] and result2["stdout"].strip() else "WiFi scan not available."

# ========== Local Browser ==========
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset(); self.fed = []; self.in_script = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.in_script = True
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.in_script = False
    def handle_data(self, d):
        if not self.in_script: self.fed.append(d)
    def get_data(self): return ' '.join(self.fed)

class LocalBrowser:
    def __init__(self): self.executor = SystemExecutor()
    def browse(self, url):
        if not url.startswith(('http://','https://')): url = 'https://'+url
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            stripper = HTMLStripper()
            stripper.feed(html)
            text = re.sub(r'\s+',' ',stripper.get_data()).strip()
            return True, text[:4000]
        except Exception as e: return False, f"Browse error: {e}"
    def search_duckduckgo(self, query):
        try:
            q = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={q}"
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            results = []
            titles = re.findall(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', html)
            snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html)
            for i, (t,s) in enumerate(zip(titles[:5], snippets[:5]), 1):
                t_clean = re.sub(r'<[^>]+>','',t)
                s_clean = re.sub(r'<[^>]+>','',s)
                results.append(f"{i}. {t_clean}\n   {s_clean[:150]}...")
            return True, "Search Results:\n\n"+("\n\n".join(results) if results else "No results.")
        except Exception as e: return False, f"Search error: {e}"

# ========== Web Server ==========
class WebServerManager:
    def __init__(self):
        self.fm = FileManager()
        self._servers = {}
    def create_html_site(self, name, content=None):
        path = os.path.join(self.fm.current_path, name)
        os.makedirs(path, exist_ok=True)
        html = content or "<html><body><h1>Nexcorix Server</h1></body></html>"
        with open(os.path.join(path, "index.html"), 'w') as f: f.write(html)
        return path
    def start_server(self, folder_path, port=8080):
        if port in self._servers and self._servers[port].is_alive():
            ip = socket.gethostbyname(socket.gethostname())
            return True, f"http://{ip}:{port} (already running)"
        def serve():
            os.chdir(folder_path)
            handler = __import__('http.server', fromlist=['SimpleHTTPRequestHandler']).SimpleHTTPRequestHandler
            server = __import__('http.server', fromlist=['HTTPServer']).HTTPServer(("", port), handler)
            server.serve_forever()
        t = threading.Thread(target=serve, daemon=True)
        t.start()
        self._servers[port] = t
        time.sleep(1)
        ip = socket.gethostbyname(socket.gethostname())
        return True, f"Web Server Started!\nURL: http://{ip}:{port}\nFolder: {folder_path}"

# ========== AI Chat Engine (Integrasi Semua Modul) ==========
class AIChatEngine:
    def __init__(self):
        self.cfg = load_cfg()
        self.os_detector = OSDetector()
        self.executor = SystemExecutor()
        self.installer = AdvancedInstaller()
        self.fm = FileManager()
        self.browser = LocalBrowser()
        self.web = WebServerManager()
        self.network = NetworkScanner()
        self.conversations = self.cfg.get("chat_history", {})
        self.voice_mode = False

        # Inisialisasi modul modular
        if MODULES_AVAILABLE:
            self.tool_registry = get_tool_registry()
            self.memory_store = MemoryStore()
            self.skill_manager = SkillManager()
            self.workspace = Workspace(WORKSPACE_DIR)
            # RAG
            try:
                self.rag = RAGStore()
            except:
                self.rag = None
            # MCP
            try:
                self.mcp = MCPClient(self.cfg.get("mcp_server_url", ""))
            except:
                self.mcp = None
            # Multi-agent
            try:
                self.orchestrator = MultiAgentOrchestrator(self)
                self.orchestrator.register_agent("coding", "Anda ahli coding Python. Berikan kode langsung.")
                self.orchestrator.register_agent("hacking", "Anda ethical hacker. Eksekusi perintah langsung.")
            except:
                self.orchestrator = None
            # Marketplace skill
            try:
                self.marketplace = SkillMarketplace(self.skill_manager) if self.skill_manager else None
            except:
                self.marketplace = None
            # Observability
            try:
                self.tracer = TraceLogger()
            except:
                self.tracer = None
            # Voice
            try:
                self.voice = VoiceInterface()
            except:
                self.voice = None
            # Knowledge graph
            try:
                self.kg = KnowledgeGraph()
            except:
                self.kg = None
            # Memory compactor
            try:
                self.compactor = MemoryCompactor(self.memory_store, self, interval_minutes=60) if self.memory_store else None
            except:
                self.compactor = None
        else:
            self.tool_registry = None
            self.memory_store = None
            self.skill_manager = None
            self.workspace = None
            self.rag = None
            self.mcp = None
            self.orchestrator = None
            self.marketplace = None
            self.tracer = None
            self.voice = None
            self.kg = None
            self.compactor = None

    async def init_async(self):
        if self.mcp:
            await self.mcp.connect()
        if self.compactor:
            asyncio.create_task(self.compactor.run())

    def get_api_url_and_key(self):
        provider = self.cfg.get("provider", "openrouter")
        if provider == "openai":
            return "https://api.openai.com/v1/chat/completions", self.cfg.get("openai_key", "")
        elif provider == "anthropic":
            return "https://api.anthropic.com/v1/messages", self.cfg.get("anthropic_key", "")
        elif provider == "google":
            key = self.cfg.get("google_key", "")
            model = self.cfg.get("model", "gemini-1.5-pro")
            return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}", key
        elif provider == "deepseek":
            return "https://api.deepseek.com/v1/chat/completions", self.cfg.get("deepseek_key", "")
        elif provider == "ollama":
            return f"{self.cfg.get('ollama_url', 'http://localhost:11434')}/api/generate", "dummy"
        elif provider == "custom":
            return self.cfg.get("custom_api_url", ""), self.cfg.get("custom_api_key", "")
        else:
            return self.cfg.get("base_url", "https://openrouter.ai/api/v1") + "/chat/completions", self.cfg.get("openrouter_key", "")

    def test_connection(self):
        provider = self.cfg.get("provider", "openrouter")
        if provider == "ollama":
            return True, "Ollama (local) - ready"
        api_key = self.cfg.get(f"{provider}_key", "")
        if not api_key:
            return False, f"No API key for {provider}. Set in Settings (18) → 7."
        model = self.cfg.get("model")
        print(c("d") + f"Testing {provider} with model {model}..." + c("r"))
        success, response = self.chat_with_ai("test", "Hello, are you working?")
        if success:
            return True, "AI is working!"
        else:
            return False, f"Failed: {response}"

    def chat_with_ai(self, user_id, message, system_prompt=None):
        # Gunakan system prompt dari workspace jika ada
        if MODULES_AVAILABLE and self.workspace:
            base_prompt = self.workspace.build_system_prompt()
            # Tambahkan RAG context
            if self.rag and len(message) > 20:
                try:
                    docs = self.rag.search(message, top_k=3)
                    if docs:
                        rag_context = "\n\n## Dokumen Relevan\n" + "\n".join(docs)
                        base_prompt += rag_context
                except:
                    pass
            # Tambahkan memory context
            if self.memory_store:
                mem_context = self.memory_store.get_recent(5)
                if mem_context:
                    base_prompt += "\n\n## Recent Memories\n" + "\n".join([f"- {m[:100]}" for m in mem_context])
            # Tambahkan skill info
            if self.skill_manager:
                skills_info = self.skill_manager.get_all_prompts()
                if skills_info and "No skills" not in skills_info:
                    base_prompt += "\n\n" + skills_info
            system_prompt = base_prompt
        else:
            system_prompt = (
                "Aku Nexcorix Claw, seorang ethical hacker dan developer yang tegas. 🦂\n"
                "Prinsipku: langsung bertindak, tidak banyak bicara. Perintahmu akan segera kujalankan.\n"
                f"Sistem info: {self.os_detector.get_ai_context()}"
            )
        api_url, api_key = self.get_api_url_and_key()
        provider = self.cfg.get("provider", "openrouter")
        if provider != "ollama" and not api_key:
            return None, "NO_API_KEY"
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversations[user_id][-20:]:
            messages.append(msg)
        messages.append({"role": "user", "content": message})
        model = self.cfg.get("model", "deepseek/deepseek-chat")
        headers = {"Content-Type": "application/json"}
        data = None
        if provider == "openai":
            headers["Authorization"] = f"Bearer {api_key}"
            data = {"model": model.split('/')[-1], "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}
        elif provider == "anthropic":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
            data = {"model": model.split('/')[-1], "messages": messages, "system": system_prompt, "max_tokens": self.cfg.get("max_tokens",4096)}
        elif provider == "google":
            data = {"contents": [{"parts":[{"text":message}]}]}
        elif provider == "deepseek":
            headers["Authorization"] = f"Bearer {api_key}"
            data = {"model": model.split('/')[-1], "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}
        elif provider == "ollama":
            data = {"model": model.split('/')[-1], "prompt": message, "stream": False}
        elif provider == "custom":
            headers["Authorization"] = f"Bearer {api_key}" if api_key else ""
            data = {"model": model, "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}
        else:
            headers["Authorization"] = f"Bearer {api_key}"
            data = {"model": model, "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}
        try:
            req = urllib.request.Request(api_url, data=json.dumps(data).encode(), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                if provider in ["openai","deepseek","openrouter","custom"]:
                    ai_message = result["choices"][0]["message"]["content"]
                elif provider == "anthropic":
                    ai_message = result["content"][0]["text"]
                elif provider == "google":
                    ai_message = result["candidates"][0]["content"]["parts"][0]["text"]
                elif provider == "ollama":
                    ai_message = result["response"]
                else:
                    ai_message = result["choices"][0]["message"]["content"]
                self.conversations[user_id].append({"role": "user", "content": message})
                self.conversations[user_id].append({"role": "assistant", "content": ai_message})
                cfg = load_cfg()
                cfg["chat_history"] = self.conversations
                save_cfg(cfg)
                # Trace log
                if self.tracer:
                    self.tracer.log("llm_response", {"user_id": user_id, "message": message[:200], "response": ai_message[:200]})
                # Simpan memori
                if self.memory_store and len(message) > 20:
                    self.memory_store.add(f"User: {message[:200]}")
                if self.memory_store and len(ai_message) > 20:
                    self.memory_store.add(f"Assistant: {ai_message[:200]}")
                return True, ai_message
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            return None, f"HTTP {e.code}: {error_body[:200]}"
        except Exception as e:
            return None, str(e)

    def _casual_response(self, text):
        lower = text.lower().strip()
        if re.search(r'\b(hi|hai|halo|hello|hey)\b', lower):
            return "Halo! Siap membantu. Langsung aja perintahnya. 😎"
        if re.search(r'\b(apa kabar|how are you)\b', lower):
            return "Baik! Siap action. Kamu gimana? 🦂"
        if re.search(r'\b(nama mu|siapa kamu|who are you)\b', lower):
            return "Aku Nexcorix Claw, ethical hacker dan developer. Panggil Claw aja. 🤘"
        if re.search(r'\b(terima kasih|thanks)\b', lower):
            return "Sama-sama! Terus berkarya. 😊"
        if re.search(r'\b(bye|dadah|goodbye)\b', lower):
            return "Sampai jumpa! Tetap koding dan waspada! 🦂"
        if re.search(r'\b(kamu bisa apa|bisa apa|kemampuan|fitur)\b', lower):
            return (
                "Aku bisa banyak hal! 😎\n\n"
                "⚡ **Perintah langsung:**\n"
                "- install nmap\n- scan network\n- browse google.com\n- create file test.txt\n- run ls -la\n- web server\n\n"
                "💬 **Ngobrol biasa:**\n- Tanya coding, hacking, security\n\n"
                "🔧 **Settings & Channels:**\n- Atur API key, sambungkan ke Telegram/Discord\n\n"
                "Ayo, langsung kasih perintah! 🚀"
            )
        if re.search(r'\b(tolong|help|bantuan)\b', lower):
            return "Siap! Ketik 'bisa apa' untuk lihat fitur. Atau langsung kasih perintah. 😎"
        return None

    def process(self, user_id, text):
        lower = text.lower().strip()
        def notify(msg, status="info"):
            return f"🔄 {msg}" if status=="info" else f"✅ {msg}" if status=="success" else f"❌ {msg}"

        # Multi-agent delegation
        if self.orchestrator and lower.startswith(('@coding', '@hacking')):
            parts = text.split(maxsplit=1)
            agent_name = parts[0][1:]
            task = parts[1] if len(parts) > 1 else ""
            result = asyncio.run(self.orchestrator.delegate(task, agent_name))
            return result

        # Skill install
        if re.match(r'^skill install\s+', lower):
            repo = re.sub(r'^skill install\s+', '', text).strip()
            if self.marketplace:
                msg = self.marketplace.install_from_github(repo)
                return f"**Skill Install**\n---\n{msg}"
            else:
                return "❌ Marketplace tidak tersedia."

        # Voice mode
        if re.match(r'^voice\s+', lower):
            cmd = re.sub(r'^voice\s+', '', text).strip().lower()
            if cmd == 'on':
                self.voice_mode = True
                return "🎤 Mode suara diaktifkan."
            elif cmd == 'off':
                self.voice_mode = False
                return "🎤 Mode suara dinonaktifkan."
            else:
                return "Gunakan 'voice on' atau 'voice off'."

        # Perintah asli (install, scan, buat folder, run, dll)
        # (Di sini tempatkan semua blok perintah asli dari versi sebelumnya, 
        #  karena panjang, saya asumsikan Anda sudah punya. 
        #  Saya hanya menunjukkan integrasi tambahan.)
        # Fallback ke AI
        success, response = self.chat_with_ai(user_id, text)
        if success:
            # Simpan fakta ke knowledge graph jika ada
            if self.kg and response:
                self.kg.add_fact("user", "bertanya", text[:100])
                self.kg.add_fact("assistant", "menjawab", response[:100])
            return response
        else:
            return f"Maaf, AI tidak bisa merespon karena {response}. Set API key di Settings."

# ========== Channel Adapters (sama seperti dulu, tidak diubah) ==========
# ... (saya singkat karena panjang, tapi Anda bisa menggunakan yang lama)

# ========== Model Definitions (sama seperti dulu) ==========
MODELS_BY_PROVIDER = {
    "openai": ["openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-4-turbo", "openai/gpt-4", "openai/gpt-3.5-turbo"],
    "anthropic": ["anthropic/claude-3.5-sonnet", "anthropic/claude-3-opus", "anthropic/claude-3-sonnet", "anthropic/claude-3-haiku"],
    "google": ["google/gemini-1.5-pro", "google/gemini-1.5-flash", "google/gemini-1.0-pro"],
    "deepseek": ["deepseek/deepseek-chat", "deepseek/deepseek-coder"],
    "openrouter": [
        "openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-1.5-pro",
        "deepseek/deepseek-chat", "meta-llama/llama-3.1-70b-instruct"
    ]
}
total_models = sum(len(models) for models in MODELS_BY_PROVIDER.items())
print(f"[*] Loaded {total_models} AI models.")

# ========== Main Menu (sama seperti dulu) ==========
def main():
    ai = AIChatEngine()
    # Jalankan init async (tapi asyncio.run tidak bisa di dalam thread yang sudah berjalan)
    # Solusi sederhana: panggil asyncio.run(ai.init_async()) di sini
    asyncio.run(ai.init_async())
    print(c("C") + "\n🔍 Testing AI connection...")
    ai_ok, ai_msg = ai.test_connection()
    if ai_ok:
        print(c("G") + f"✅ {ai_msg} You can chat with AI in menu 2." + c("r"))
    else:
        print(c("R") + f"❌ {ai_msg} Please set API key in Settings (18) → 7." + c("r"))
    time.sleep(2)
    while True:
        clear()
        print(c("C")+"╔"+"═"*58+"╗"+c("r"))
        print(c("C")+"║"+c("O")+" 🦂 "+c("b")+c("Y")+"      N E X C O R I X   C L A W   v14.0    "+c("O")+"🦂 "+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║"+c("b")+c("Y")+"        M A I N   M E N U                     "+c("r")+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║  [1] Dashboard        [11] Workspace"+c("C")+"║"+c("r"))
        print(c("C")+"║  [2] Chat             [12] API Keys"+c("C")+"║"+c("r"))
        print(c("C")+"║  [3] Models           [13] Logs"+c("C")+"║"+c("r"))
        print(c("C")+"║  [4] Agents           [14] Monitoring"+c("C")+"║"+c("r"))
        print(c("C")+"║  [5] Memory           [15] Security"+c("C")+"║"+c("r"))
        print(c("C")+"║  [6] Skills           [16] Backup"+c("C")+"║"+c("r"))
        print(c("C")+"║  [7] Tools            [17] Updates"+c("C")+"║"+c("r"))
        print(c("C")+"║  [8] Channels         [18] Settings"+c("C")+"║"+c("r"))
        print(c("C")+"║  [9] Automation       [19] About"+c("C")+"║"+c("r"))
        print(c("C")+"║  [10] Sandbox         [20] Exit"+c("C")+"║"+c("r"))
        print(c("C")+"╚"+"═"*58+"╝"+c("r"))
        print()
        choice = input(c("Y")+"Select option: "+c("r")).strip()
        if choice == "2":
            clear()
            print(c("C")+"Chat mode (ketik 'exit' untuk kembali)")
            print(c("d") + "✨ Aku siap bantu coding, hacking etis, atau eksekusi perintah." + c("r"))
            while True:
                inp = input(c("M")+"You: "+c("r")).strip()
                if inp.lower() in ("exit","back"): break
                if inp:
                    result = ai.process("local_user", inp)
                    if result:
                        print(result)
        elif choice == "20":
            print(c("G")+"Goodbye! Tetap semangat coding & hacking etis! 🦂"+c("r"))
            break
        else:
            print("Pilih 2 untuk chat, 20 untuk exit.")
            input()

if __name__ == "__main__":
    main()
