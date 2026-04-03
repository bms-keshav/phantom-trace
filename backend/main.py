from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response

try:
    from .dossier import generate_dossier_pdf
    from .graph import build_graph, compute_graph_metrics
    from .parser import parse_logs
    from .scoring import score_all_nodes
    from .sigma import generate_sigma_rule
except ImportError:
    from dossier import generate_dossier_pdf
    from graph import build_graph, compute_graph_metrics
    from parser import parse_logs
    from scoring import score_all_nodes
    from sigma import generate_sigma_rule

app = FastAPI(title="PHANTOM TRACE API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LAST_ANALYSIS: dict[str, Any] = {
    "scores": [],
    "df": None,
    "graph": None,
}


def _build_timeline(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []

    temp = df.copy()
    temp["bucket"] = temp["timestamp"].dt.floor("min")
    counts = temp.groupby("bucket").size().reset_index(name="request_count")
    return [
        {
            "timestamp": row["bucket"].isoformat(),
            "request_count": int(row["request_count"]),
        }
        for _, row in counts.iterrows()
    ]


def _serialize_graph(g, scores: list[dict]) -> dict:
    score_map = {s["node"]: s for s in scores}
    out_degree = dict(g.out_degree(weight="weight"))

    nodes = []
    for n in g.nodes():
        node_score = score_map.get(n, {})
        nodes.append(
            {
                "id": n,
                "score": float(node_score.get("final_score", 0.0)),
                "confidence_pct": float(node_score.get("confidence_pct", 0.0)),
                "out_degree": float(out_degree.get(n, 0.0)),
                "request_count": int(node_score.get("request_count", 0)),
            }
        )

    links = []
    for src, dst, data in g.edges(data=True):
        links.append(
            {
                "source": src,
                "target": dst,
                "weight": int(data.get("weight", 1)),
                "first_seen_ts": float(data.get("first_seen_ts", 0.0)),
                "last_seen_ts": float(data.get("last_seen_ts", 0.0)),
            }
        )

    return {"nodes": nodes, "links": links}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = parse_logs(content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse logs: {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="No valid log rows parsed")

    g = build_graph(df)
    metrics = compute_graph_metrics(g)
    scores = score_all_nodes(g, df, metrics)

    if not scores:
        raise HTTPException(status_code=400, detail="Not enough data to score nodes")

    LAST_ANALYSIS["scores"] = scores
    LAST_ANALYSIS["df"] = df
    LAST_ANALYSIS["graph"] = g

    return {
        "top_node": scores[0],
        "ranked_nodes": scores[:10],
        "all_nodes": scores,
        "graph": _serialize_graph(g, scores),
        "timeline": _build_timeline(df),
        "summary_stats": {
            "total_nodes": g.number_of_nodes(),
            "total_edges": g.number_of_edges(),
            "total_requests": int(len(df)),
        },
    }


@app.get("/api/node/{ip}/sigma")
def get_sigma_rule(ip: str):
    scores = LAST_ANALYSIS.get("scores", [])
    node_data = next((s for s in scores if s.get("node") == ip), None)
    if node_data is None:
        raise HTTPException(status_code=404, detail="Node not found in latest analysis")

    rule = generate_sigma_rule(node_data)
    return PlainTextResponse(content=rule)


@app.get("/api/node/{ip}/dossier")
def get_dossier(ip: str):
    scores = LAST_ANALYSIS.get("scores", [])
    df = LAST_ANALYSIS.get("df")

    if df is None:
        raise HTTPException(status_code=404, detail="No analysis found. Run /api/analyze first.")

    node_data = next((s for s in scores if s.get("node") == ip), None)
    if node_data is None:
        raise HTTPException(status_code=404, detail="Node not found in latest analysis")

    target_counts = (
        df[df["src_ip"] == ip]["dst_ip"].value_counts().head(5).index.tolist()
    )
    sigma_rule = generate_sigma_rule(node_data)
    pdf_bytes = generate_dossier_pdf(node_data, sigma_rule, target_counts)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=phantom_trace_{ip}.pdf"},
    )
