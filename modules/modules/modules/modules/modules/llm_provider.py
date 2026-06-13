import json
import urllib.request
import urllib.error

class LLMProvider:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.provider = cfg.get("provider", "openrouter")
        self.model = cfg.get("model", "openai/gpt-3.5-turbo")
    def get_api_url_and_key(self):
        if self.provider == "openai":
            return "https://api.openai.com/v1/chat/completions", self.cfg.get("openai_key", "")
        elif self.provider == "anthropic":
            return "https://api.anthropic.com/v1/messages", self.cfg.get("anthropic_key", "")
        elif self.provider == "google":
            key = self.cfg.get("google_key", "")
            model = self.model.replace("google/", "")
            return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}", key
        elif self.provider == "deepseek":
            return "https://api.deepseek.com/v1/chat/completions", self.cfg.get("deepseek_key", "")
        else:
            return "https://openrouter.ai/api/v1/chat/completions", self.cfg.get("openrouter_key", "")
    async def chat(self, user_msg: str, system_prompt: str = "") -> str:
        url, key = self.get_api_url_and_key()
        if not key:
            return "API key tidak diatur. Silakan set di menu Settings."
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        model = self.model
        if self.provider == "openrouter" and "/" not in model:
            model = f"openai/{model}"
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            "temperature": self.cfg.get("temperature", 0.7),
            "max_tokens": self.cfg.get("max_tokens", 4096)
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {e}"
    def test_connection(self):
        # Sinkron test
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resp = loop.run_until_complete(self.chat("ping", ""))
            loop.close()
            if "Error" not in resp:
                return True, "Koneksi AI berhasil"
            else:
                return False, resp
        except Exception as e:
            return False, str(e)
