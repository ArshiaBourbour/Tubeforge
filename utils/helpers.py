from __future__ import annotations

import platform
import sys
from datetime import datetime

try:
    import psutil

    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def system_info() -> dict[str, str]:
    """Live system info panel data (CPU, RAM, OS, Python version)."""
    cpu = "N/A"
    ram = "N/A"
    if _HAS_PSUTIL:
        try:
            cpu = f"{psutil.cpu_percent(interval=0.1):.0f}%"
            mem = psutil.virtual_memory()
            ram = f"{mem.percent:.0f}% ({human_gb(mem.used)} / {human_gb(mem.total)})"
        except Exception:
            pass
    return {
        "OS": f"{platform.system()} {platform.release()}",
        "Python": sys.version.split()[0],
        "CPU": cpu,
        "RAM": ram,
    }


def human_gb(num_bytes: float) -> str:
    return f"{num_bytes / (1024 ** 3):.1f} GB"


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


def truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[: max(0, width - 1)] + "…"
