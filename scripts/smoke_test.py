import json
from pathlib import Path
from urllib import request


def _post_analyze(path: Path) -> dict:
    boundary = "----PhantomTraceBoundary"
    data = path.read_bytes()

    body = []
    body.append(f"--{boundary}\r\n".encode())
    body.append(
        b'Content-Disposition: form-data; name="file"; filename="sample_logs.json"\r\n'
    )
    body.append(b"Content-Type: application/json\r\n\r\n")
    body.append(data)
    body.append(f"\r\n--{boundary}--\r\n".encode())

    payload = b"".join(body)

    req = request.Request(
        "http://127.0.0.1:8000/api/analyze",
        data=payload,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(url: str) -> str:
    with request.urlopen(url, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> None:
    sample = Path("data/sample_logs.json")
    if not sample.exists():
        raise SystemExit("Missing data/sample_logs.json. Run: python data/generate_logs.py")

    health = _get("http://127.0.0.1:8000/api/health")
    print("health:", health)

    result = _post_analyze(sample)
    analysis_id = result.get("analysis_id")
    if not analysis_id:
        raise SystemExit("Missing analysis_id in /api/analyze response")

    top = result["top_node"]
    print("top_node:", top["node"], "score:", top["final_score"], "confidence:", top["confidence_pct"])

    sigma = _get(
        f"http://127.0.0.1:8000/api/node/{top['node']}/sigma?analysis_id={analysis_id}"
    )
    print("sigma_ok:", "title:" in sigma and "detection:" in sigma)

    print("summary:", result["summary_stats"])


if __name__ == "__main__":
    main()
