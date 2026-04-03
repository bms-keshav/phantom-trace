from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

STORE_DIR = Path(tempfile.gettempdir()) / "phantom_trace_analyses"
STORE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TTL_SECONDS = 4 * 60 * 60
_STORE_LOCK = Lock()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _analysis_path(analysis_id: str) -> Path:
    return STORE_DIR / f"{analysis_id}.json"


def purge_expired_records(ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
    cutoff = _utc_now() - timedelta(seconds=ttl_seconds)

    with _STORE_LOCK:
        for file_path in STORE_DIR.glob("*.json"):
            try:
                if datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc) < cutoff:
                    file_path.unlink(missing_ok=True)
            except OSError:
                continue


def create_analysis_record(payload: dict, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
    purge_expired_records(ttl_seconds=ttl_seconds)

    analysis_id = uuid4().hex
    record = {
        "analysis_id": analysis_id,
        "created_at": _utc_now().isoformat(),
        **payload,
    }

    target = _analysis_path(analysis_id)
    temp = target.with_suffix(".tmp")

    with _STORE_LOCK:
        temp.write_text(json.dumps(record), encoding="utf-8")
        temp.replace(target)

    return analysis_id


def get_analysis_record(analysis_id: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> dict | None:
    if not analysis_id:
        return None

    path = _analysis_path(analysis_id)
    if not path.exists():
        return None

    with _STORE_LOCK:
        try:
            raw = path.read_text(encoding="utf-8")
            record = json.loads(raw)
        except (OSError, json.JSONDecodeError):
            return None

    created_at_raw = record.get("created_at")
    try:
        created_at = datetime.fromisoformat(created_at_raw)
    except (TypeError, ValueError):
        created_at = None

    if created_at is None or (_utc_now() - created_at) > timedelta(seconds=ttl_seconds):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return None

    return record
