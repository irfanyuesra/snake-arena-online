"""Small shared helpers."""

from __future__ import annotations

import secrets
import time


def now_ms() -> int:
    return int(time.time() * 1000)


def gen_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(4)}"
