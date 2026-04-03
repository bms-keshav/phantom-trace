import ast
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_FIELDS = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "endpoint",
    "method",
    "headers",
    "status_code",
    "latency_ms",
    "payload_size",
]


DEFAULTS = {
    "endpoint": "/unknown",
    "method": "GET",
    "headers": {},
    "status_code": 0,
    "latency_ms": 0,
    "payload_size": 0,
}


def _load_field_map() -> dict[str, list[str]]:
    field_map_path = Path(__file__).resolve().parents[1] / "data" / "field_map.json"
    if not field_map_path.exists():
        return {k: [k] for k in REQUIRED_FIELDS}
    return json.loads(field_map_path.read_text(encoding="utf-8"))


def _read_bytes(source: Any) -> bytes:
    if isinstance(source, (str, Path)):
        return Path(source).read_bytes()
    if isinstance(source, bytes):
        return source
    if hasattr(source, "read"):
        data = source.read()
        return data if isinstance(data, bytes) else str(data).encode("utf-8")
    raise TypeError("Unsupported log source. Provide a path, bytes, or file-like object.")


def _detect_format(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace").strip()
    if not text:
        raise ValueError("Input log payload is empty")
    if text.startswith("["):
        return "json"
    if text.startswith("{"):
        return "ndjson"
    return "csv"


def _read_raw_dataframe(raw: bytes) -> pd.DataFrame:
    fmt = _detect_format(raw)
    text = raw.decode("utf-8", errors="replace")

    if fmt == "json":
        records = json.loads(text)
        return pd.DataFrame(records)

    if fmt == "ndjson":
        rows = []
        for line in text.splitlines():
            s = line.strip()
            if s:
                rows.append(json.loads(s))
        return pd.DataFrame(rows)

    sample = text[:4096]
    delimiters = [",", ";", "\t", "|"]
    delim = max(delimiters, key=sample.count)
    return pd.read_csv(io.StringIO(text), sep=delim)


def _normalize_columns(df: pd.DataFrame, field_map: dict[str, list[str]]) -> pd.DataFrame:
    rename_map = {}
    available = {c.lower(): c for c in df.columns}

    for canonical, aliases in field_map.items():
        for alias in aliases:
            if alias.lower() in available:
                rename_map[available[alias.lower()]] = canonical
                break

    out = df.rename(columns=rename_map).copy()

    for field in REQUIRED_FIELDS:
        if field not in out.columns:
            out[field] = DEFAULTS.get(field)

    return out[REQUIRED_FIELDS]


def _coerce_headers(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return {}
        try:
            loaded = json.loads(s)
            return loaded if isinstance(loaded, dict) else {}
        except json.JSONDecodeError:
            try:
                loaded = ast.literal_eval(s)
                return loaded if isinstance(loaded, dict) else {}
            except (ValueError, SyntaxError):
                return {}
    return {}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_logs(source: Any) -> pd.DataFrame:
    """
    Parse JSON array, NDJSON, or CSV logs and normalize to a standard schema.
    """
    raw = _read_bytes(source)
    frame = _read_raw_dataframe(raw)
    field_map = _load_field_map()
    df = _normalize_columns(frame, field_map)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp", "src_ip", "dst_ip"]).copy()

    df["headers"] = df["headers"].apply(_coerce_headers)
    df["user_agent"] = df["headers"].apply(lambda h: str(h.get("User-Agent", "")))

    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce").fillna(0).astype(int)
    df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce").fillna(0.0)
    df["payload_size"] = pd.to_numeric(df["payload_size"], errors="coerce").fillna(0.0)

    # Order-insensitive content signature (keys + values sorted).
    df["header_signature"] = df["headers"].apply(
        lambda h: _sha256_text(
            "|".join(sorted(str(k) for k in h.keys()))
            + "::"
            + "|".join(sorted(str(v) for v in h.values()))
        )
    )

    # Order-preserving signature used for bot-like header ordering patterns.
    df["header_order_signature"] = df["headers"].apply(
        lambda h: _sha256_text("|".join(str(k) for k in h.keys()))
    )

    df["ua_hash"] = df["user_agent"].apply(_sha256_text)
    df["timestamp_epoch_s"] = df["timestamp"].astype("int64") / 1_000_000_000.0

    df = df.sort_values(["src_ip", "timestamp"]).copy()
    df["inter_arrival_time"] = (
        df.groupby("src_ip")["timestamp_epoch_s"].diff().fillna(0.0)
    )

    return df.reset_index(drop=True)
