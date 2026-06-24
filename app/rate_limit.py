from collections import defaultdict, deque
from datetime import datetime, timedelta
from threading import Lock

from fastapi import HTTPException, Request


_attempts: dict[str, deque[datetime]] = defaultdict(deque)
_lock = Lock()


def enforce_rate_limit(
    request: Request,
    scope: str,
    limit: int,
    window_seconds: int,
    subject: str = "",
) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"{scope}:{client_host}:{subject.lower()}"
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=window_seconds)
    with _lock:
        bucket = _attempts[key]
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            retry_after = max(int((bucket[0] + timedelta(seconds=window_seconds) - now).total_seconds()), 1)
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )
        bucket.append(now)


def clear_rate_limits() -> None:
    with _lock:
        _attempts.clear()
