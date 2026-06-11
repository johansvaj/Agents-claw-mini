import os
import json
from datetime import datetime

class TraceLogger:
    def __init__(self, log_dir: str = "~/.nexcorix/logs"):
        self.log_dir = os.path.expanduser(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
    def log(self, event: str, data: dict):
        entry = {"timestamp": datetime.now().isoformat(), "event": event, "data": data}
        filename = f"{datetime.now().strftime('%Y%m%d')}.jsonl"
        path = os.path.join(self.log_dir, filename)
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    def get_recent(self, limit=50):
        traces = []
        for f in sorted(os.listdir(self.log_dir), reverse=True):
            if f.endswith(".jsonl"):
                with open(os.path.join(self.log_dir, f)) as fp:
                    for line in fp:
                        traces.append(json.loads(line))
                        if len(traces) >= limit:
                            return traces
        return traces
