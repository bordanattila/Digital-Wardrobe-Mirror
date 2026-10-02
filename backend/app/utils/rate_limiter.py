from collections import defaultdict
from time import time

from fastapi import HTTPException, Request

_hits: dict[str, list[float]] = defaultdict(list)
MAX_HITS = 10
WINDOW = 60  # seconds


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time()
    window = _hits[ip]
    _hits[ip] = [t for t in window if now - t < WINDOW]
    if len(_hits[ip]) >= MAX_HITS:
        raise HTTPException(status_code=429, detail="Too many requests")
    _hits[ip].append(now)
