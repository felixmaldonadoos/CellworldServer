"""
Compare the performance of two logger implementations:

• LoggerOld  – simple version using print + string join
• LoggerFast – optimized version using sys.stdout.write, __slots__, etc.

Both run the same sequence of log calls `REPEAT` times with stdout
redirected to an in-memory buffer so console I/O latency does not dominate.
"""

import sys
import time
import io
from contextlib import redirect_stdout
from typing import Any, Dict

# ───────────────────────── LoggerOld ───────────────────────────────────────────
class LoggerOld:
    _COLORS = {
        "LOG": "",
        "SUCCESS": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "RESET": "\033[0m",
    }

    def __init__(self, header: str = "Default"):
        self.header = header

    def _write(self, level: str, msg: str='', *args, subheader: str | None = None, **kw):
        color = self._COLORS[level]
        reset = self._COLORS["RESET"]
        parts = [f"[{self.header}]"]
        if subheader:
            parts.append(f"[{subheader}]")
        parts.append(msg)
        parts.extend(map(str, args))
        parts.extend(f"{k}={v} |" for k, v in kw.items())
        print(f"{color}{' '.join(parts)}{reset}")

    def log(self, msg: str, *a, subheader=None, **k):      self._write("LOG",     msg, *a, subheader=subheader, **k)
    def success(self, msg: str, *a, subheader=None, **k):  self._write("SUCCESS", msg, *a, subheader=subheader, **k)
    def warning(self, msg: str, *a, subheader=None, **k):  self._write("WARNING", msg, *a, subheader=subheader, **k)
    def error(self, msg: str, *a, subheader=None, **k):    self._write("ERROR",   msg, *a, subheader=subheader, **k)

# ───────────────────────── LoggerFast ──────────────────────────────────────────
class Logger:
    """
    Minimal-overhead ANSI logger for real-time services.
    """
    __slots__ = ("header", "_prefix")

    _COLORS: Dict[str, str] = {
        "LOG": "",
        "SUCCESS": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "RESET": "\033[0m",
    }

    def __init__(self, header: str = "Default") -> None:
        self.header = header
        self._prefix = f"[{header}]"

    def _write(
        self,
        level: str,
        msg: str,
        *args: Any,
        subheader: str | None = None,
        **kw: Any,
    ) -> None:
        color = self._COLORS[level]
        reset = self._COLORS["RESET"]
        head = f"{color}{self._prefix}"
        if subheader:
            head += f"[{subheader}]"
        head += " "

        if not args and not kw:
            sys.stdout.write(f"{head}{msg}{reset}\n")
            return

        parts: list[str] = [msg]
        if args:
            parts.extend(map(str, args))
        if kw:
            parts.extend(f"| {k}={v}" for k, v in kw.items())
        sys.stdout.write(f"{head}{' '.join(parts)}{reset}\n")

    # public
    def log(self, msg: str='', *a, subheader=None, **k):     self._write("LOG",     msg, *a, subheader=subheader, **k)
    def success(self, msg: str='', *a, subheader=None, **k): self._write("SUCCESS", msg, *a, subheader=subheader, **k)
    def warning(self, msg: str='', *a, subheader=None, **k): self._write("WARNING", msg, *a, subheader=subheader, **k)
    def error(self, msg: str='', *a, subheader=None, **k):   self._write("ERROR",   msg, *a, subheader=subheader, **k)

# ───────────────────────── Benchmark helper ────────────────────────────────────
def run_cases(LoggerCls):
    srv = LoggerCls("Srv")
    srv.log("boot OK")
    srv.success("client connected", "192.168.1.42", subheader="Net")
    srv.warning("latency", 240, "ms", subheader="Net")
    srv.error("timeout", peer="192.168.1.42", subheader="Net")

    auth = LoggerCls("Auth")
    auth.log("login", user="alice")
    auth.success("jwt issued", user="alice")
    auth.warning("passwd retry", user="bob", left=2)
    auth.error("account lock", user="eve", reason="too many retries")

def benchmark(LoggerCls, repeat: int) -> float:
    sink = io.StringIO()
    start = time.perf_counter()
    with redirect_stdout(sink):
        for _ in range(repeat):
            run_cases(LoggerCls)
    end = time.perf_counter()
    return end - start

if __name__ == "__main__":
    REPEAT = 10_000  # adjust for your machine

    t_old  = benchmark(LoggerOld,  REPEAT)
    t_fast = benchmark(Logger, REPEAT)

    print(f"Iterations      : {REPEAT}")
    print(f"LoggerOld  time : {t_old:.4f} s")
    print(f"LoggerFast time : {t_fast:.4f} s")
    print(f"Speed-up        : {t_old / t_fast:.2f}×")

    show_examples = True
    if show_examples:
        print('\n== Examples ==\n')
        srv = Logger("Srv")
        srv.log("boot OK")
        srv.success("client connected", "192.168.1.42", subheader="Net")
        srv.warning("latency", 240, "ms", subheader="Net")
        srv.error("timeout", peer="192.168.1.42", subheader="Net")

        auth = Logger("Auth")
        auth.log("login", user="alice")
        auth.success("jwt issued", user="alice")
        auth.warning("passwd retry", user="bob", left=2)
        auth.error("account lock", user="eve", reason="too many retries")