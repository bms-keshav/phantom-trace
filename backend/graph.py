from __future__ import annotations

import networkx as nx
import pandas as pd


def build_graph(df: pd.DataFrame) -> nx.DiGraph:
    g = nx.DiGraph()

    for (src, dst), group in df.groupby(["src_ip", "dst_ip"]):
        g.add_edge(
            src,
            dst,
            weight=int(len(group)),
            avg_latency=float(group["latency_ms"].mean()),
            timestamps=group["timestamp_epoch_s"].tolist(),
            first_seen_ts=float(group["timestamp_epoch_s"].min()),
            last_seen_ts=float(group["timestamp_epoch_s"].max()),
            header_sigs=group["header_signature"].tolist(),
            ua_hashes=group["ua_hash"].tolist(),
        )

    return g


def compute_graph_metrics(g: nx.DiGraph) -> dict:
    if g.number_of_nodes() == 0:
        return {
            "pagerank": {},
            "betweenness": {},
            "out_degree": {},
            "eigenvector": {},
        }

    pagerank = nx.pagerank(g, weight="weight")
    betweenness = nx.betweenness_centrality(g, weight="weight")
    out_degree = dict(g.out_degree(weight="weight"))

    try:
        eigenvector = nx.eigenvector_centrality(g, weight="weight", max_iter=500)
    except Exception:
        eigenvector = {n: 0.0 for n in g.nodes()}

    return {
        "pagerank": pagerank,
        "betweenness": betweenness,
        "out_degree": out_degree,
        "eigenvector": eigenvector,
    }
