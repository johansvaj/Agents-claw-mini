"""Security sandbox for Agents Claw Mini."""

import logging
import resource
import signal
from typing import Any, Dict, List, Optional, Callable
from contextlib import contextmanager
from .config import SandboxConfig
from .exceptions import SandboxException

logger = logging.getLogger("AgentsClawMini.Sandbox")

class Sandbox:
    """
    Security sandbox untuk eksekusi kode yang aman.

    Features:
    - Timeout enforcement
    - Memory limits
    - Module restrictions
    - Code isolation
    - Safe eval/exec

    Digunakan untuk:
    - Menjalankan user code
    - Tool execution
    - Plugin system
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()

    @contextmanager
    def _timeout_context(self, seconds: int):
        """Context manager untuk timeout."""
        def handler(signum, frame):
            raise TimeoutError(f"Execution exceeded {seconds} seconds")

        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            yield

    def _limit_memory(self, max_mb: int):
        """Limit memory usage."""
        if hasattr(resource, 'RLIMIT_AS'):
            max_bytes = max_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))

    def execute(self, code: str, globals_dict: Optional[Dict] = None, 
                locals_dict: Optional[Dict] = None) -> Any:
        """Execute code in sandbox."""
        if not self.config.enabled:
            return exec(code, globals_dict or {}, locals_dict or {})

        try:
            with self._timeout_context(self.config.max_execution_time):
                # Create restricted globals
                safe_globals = {
                    "__builtins__": {
                        "abs": abs, "all": all, "any": any, "ascii": ascii,
                        "bin": bin, "bool": bool, "bytearray": bytearray,
                        "bytes": bytes, "chr": chr, "dict": dict, "divmod": divmod,
                        "enumerate": enumerate, "filter": filter, "float": float,
                        "format": format, "frozenset": frozenset, "hash": hash,
                        "hex": hex, "int": int, "isinstance": isinstance,
                        "issubclass": issubclass, "iter": iter, "len": len,
                        "list": list, "map": map, "max": max, "min": min,
                        "next": next, "oct": oct, "ord": ord, "pow": pow,
                        "print": print, "range": range, "repr": repr,
                        "reversed": reversed, "round": round, "set": set,
                        "slice": slice, "sorted": sorted, "str": str,
                        "sum": sum, "tuple": tuple, "type": type, "zip": zip,
                    }
                }

                if globals_dict:
                    safe_globals.update(globals_dict)

                # Limit memory
                self._limit_memory(self.config.max_memory_mb)

                return exec(code, safe_globals, locals_dict or {})

        except TimeoutError as e:
            raise SandboxException(f"Timeout: {e}")
        except MemoryError:
            raise SandboxException(f"Memory limit exceeded ({self.config.max_memory_mb}MB)")
        except Exception as e:
            raise SandboxException(f"Sandbox error: {e}")

    def evaluate(self, expression: str, globals_dict: Optional[Dict] = None) -> Any:
        """Safely evaluate expression."""
        if not self.config.enabled:
            return eval(expression, globals_dict or {})

        safe_globals = {
            "__builtins__": {
                "abs": abs, "max": max, "min": min, "sum": sum,
                "len": len, "round": round, "pow": pow,
            }
        }
        if globals_dict:
            safe_globals.update(globals_dict)

        try:
            with self._timeout_context(self.config.max_execution_time):
                return eval(expression, safe_globals)
        except Exception as e:
            raise SandboxException(f"Eval error: {e}")

    def run_function(self, func: Callable, *args, **kwargs) -> Any:
        """Run function in sandbox."""
        try:
            with self._timeout_context(self.config.max_execution_time):
                return func(*args, **kwargs)
        except TimeoutError as e:
            raise SandboxException(f"Timeout: {e}")
        except Exception as e:
            raise SandboxException(f"Function error: {e}")

    def __repr__(self):
        return f"Sandbox(enabled={self.config.enabled}, max_time={self.config.max_execution_time}s)"
