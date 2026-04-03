from __future__ import annotations

import networkx as nx
import pandas as pd

try:
    from .beacon import compute_beacon_score
    from .fingerprint import compute_fingerprint_score
except ImportError:
    from beacon import compute_beacon_score
    from fingerprint import compute_fingerprint_score


def _normalize_map(values: dict) -> dict:
    if not values:
        return {}
    nums = list(values.values())
    lo = min(nums)
    hi = max(nums)
    if hi - lo < 1e-12:
        return {k: 0.0 for k in values}
    return {k: (v - lo) / (hi - lo) for k, v in values.items()}


def _normalize_value(value: float, lo: float, hi: float) -> float:
    if hi - lo < 1e-12:
        return 0.0
    return (value - lo) / (hi - lo)


def score_all_nodes(g: nx.DiGraph, df: pd.DataFrame, graph_metrics: dict) -> list[dict]:
    results = []
    grouped_by_src = {src: grp for src, grp in df.groupby("src_ip", sort=False)}

    pagerank_n = _normalize_map(graph_metrics.get("pagerank", {}))
    betweenness_n = _normalize_map(graph_metrics.get("betweenness", {}))
    eigenvector_n = _normalize_map(graph_metrics.get("eigenvector", {}))

    request_counts = {src: int(len(grp)) for src, grp in grouped_by_src.items()}
    if request_counts:
        rc_lo, rc_hi = min(request_counts.values()), max(request_counts.values())
    else:
        rc_lo, rc_hi = 0, 1

    total_nodes = max(g.number_of_nodes(), 1)

    for node in g.nodes():
        node_df = grouped_by_src.get(node)
        if node_df is None or len(node_df) < 3:
            continue

        centrality = (
            0.4 * pagerank_n.get(node, 0.0)
            + 0.3 * betweenness_n.get(node, 0.0)
            + 0.3 * eigenvector_n.get(node, 0.0)
        )

        timestamps = node_df["timestamp_epoch_s"].tolist()
        beacon = compute_beacon_score(timestamps)

        fp = compute_fingerprint_score(node_df)

        neighbors = list(g.successors(node))
        coordination = len(neighbors) / total_nodes

        volume = _normalize_value(float(request_counts.get(node, 0)), float(rc_lo), float(rc_hi))

        final_score = (
            0.20 * centrality
            + 0.40 * beacon["score"]
            + 0.30 * fp["fingerprint_score"]
            + 0.10 * coordination
        )

        results.append(
            {
                "node": node,
                "final_score": round(float(final_score), 4),
                "confidence_pct": round(float(final_score) * 100, 1),
                "breakdown": {
                    "centrality": round(float(centrality), 4),
                    "beacon": beacon["score"],
                    "fingerprint": fp["fingerprint_score"],
                    "coordination": round(float(coordination), 4),
                    "volume": round(float(volume), 4),
                },
                "beacon_detail": beacon,
                "fingerprint_detail": fp,
                "request_count": int(len(node_df)),
                "unique_destinations": int(node_df["dst_ip"].nunique()),
                "suspected": final_score >= 0.7,
            }
        )

    results.sort(key=lambda x: x["final_score"], reverse=True)

    if len(results) >= 2 and results[0]["final_score"] > 0:
        gap = results[0]["final_score"] - results[1]["final_score"]
        results[0]["attribution_confidence"] = round(gap / results[0]["final_score"], 4)
    elif len(results) == 1:
        results[0]["attribution_confidence"] = 1.0

    return results
