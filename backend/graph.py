from __future__ import annotations

import networkx as nx
import pandas as pd


def build_graph(df: pd.DataFrame) -> nx.DiGraph:
    g = nx.DiGraph()

    edge_stats = (
        df.groupby(["src_ip", "dst_ip"], sort=False)
        .agg(
            weight=("timestamp_epoch_s", "size"),
            avg_latency=("latency_ms", "mean"),
            timestamps=("timestamp_epoch_s", list),
            first_seen_ts=("timestamp_epoch_s", "min"),
            last_seen_ts=("timestamp_epoch_s", "max"),
            header_sigs=("header_signature", list),
            ua_hashes=("ua_hash", list),
        )
        .reset_index()
    )

    for row in edge_stats.itertuples(index=False):
        g.add_edge(
            row.src_ip,
            row.dst_ip,
            weight=int(row.weight),
            avg_latency=float(row.avg_latency),
            timestamps=row.timestamps,
            first_seen_ts=float(row.first_seen_ts),
            last_seen_ts=float(row.last_seen_ts),
            header_sigs=row.header_sigs,
            ua_hashes=row.ua_hashes,
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
    if g.number_of_nodes() > 120:
        betweenness = nx.betweenness_centrality(g, weight="weight", k=100, seed=42)
    else:
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
