import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4


def _random_headers() -> dict:
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "curl/8.5.0",
        "python-requests/2.32.3",
    ]
    return {
        "User-Agent": random.choice(uas),
        "Accept": random.choice(["application/json", "*/*"]),
        "X-Request-ID": str(uuid4()),
        "Accept-Encoding": random.choice(["gzip", "br", "gzip, deflate"]),
    }


def _random_endpoint() -> str:
    endpoints = [
        "/api/v1/status",
        "/api/v1/users",
        "/api/v1/orders",
        "/api/v1/metrics",
        "/internal/health",
        "/admin/audit",
    ]
    return random.choice(endpoints)


def generate_logs(total_entries: int = 5000, seed: int = 42) -> list[dict]:
    random.seed(seed)

    start = datetime(2024, 3, 15, 14, 0, 0, tzinfo=timezone.utc)

    internal_nodes = [f"10.0.{a}.{b}" for a in range(1, 5) for b in range(1, 16)]
    hidden_c2 = "10.4.2.11"

    if hidden_c2 not in internal_nodes:
        internal_nodes.append(hidden_c2)

    non_c2_nodes = [n for n in internal_nodes if n != hidden_c2]
    c2_targets = set(random.sample(non_c2_nodes, k=max(1, int(0.6 * len(non_c2_nodes)))))

    # Build C2 traffic: near-periodic requests every ~12 seconds with very low variance.
    c2_events = []
    c2_count = max(300, int(total_entries * 0.2))
    t = start + timedelta(seconds=1)
    ordered_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Accept": "application/json",
        "X-Request-ID": "static-c2-pattern",
        "Accept-Encoding": "gzip",
    }

    c2_target_list = list(c2_targets)
    for i in range(c2_count):
        delta = random.gauss(12.0, 0.22)
        t += timedelta(seconds=delta)
        dst = c2_target_list[i % len(c2_target_list)]
        c2_events.append(
            {
                "timestamp": t.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                "src_ip": hidden_c2,
                "dst_ip": dst,
                "endpoint": "/api/v1/status",
                "method": "GET",
                "headers": dict(ordered_headers),
                "status_code": 200,
                "latency_ms": random.randint(40, 120),
                "payload_size": random.randint(120, 640),
            }
        )

    # Background traffic: noisier and less regular.
    normal_events = []
    normal_count = total_entries - len(c2_events)
    current = start + timedelta(seconds=40)
    for _ in range(normal_count):
        current += timedelta(seconds=random.uniform(0.2, 3.5))
        src = random.choice(non_c2_nodes)
        dst = random.choice([n for n in internal_nodes if n != src])
        status = random.choices([200, 201, 204, 400, 401, 403, 404, 500], weights=[40, 8, 8, 12, 8, 6, 10, 8])[0]

        normal_events.append(
            {
                "timestamp": current.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                "src_ip": src,
                "dst_ip": dst,
                "endpoint": _random_endpoint(),
                "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                "headers": _random_headers(),
                "status_code": status,
                "latency_ms": random.randint(35, 900),
                "payload_size": random.randint(64, 8192),
            }
        )

    logs = normal_events + c2_events
    logs.sort(key=lambda r: r["timestamp"])
    return logs


def main() -> None:
    base = Path(__file__).resolve().parent
    out_path = base / "sample_logs.json"
    data = generate_logs()
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Generated {len(data)} records at {out_path}")


if __name__ == "__main__":
    main()
