import time
import threading
import schedule
from typing import Callable

class CronService:
    def __init__(self):
        self._running = False
        self._thread = None
    def add_job(self, func: Callable, interval_seconds: int):
        schedule.every(interval_seconds).seconds.do(func)
    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    def _run(self):
        while self._running:
            schedule.run_pending()
            time.sleep(1)
    def stop(self):
        self._running = False
