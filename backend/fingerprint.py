from __future__ import annotations

import hashlib

import pandas as pd


def compute_fingerprint_score(df_node: pd.DataFrame) -> dict:
    """
    Analyze per-node metadata consistency.
    High repetition in header ordering and low UA diversity can indicate automation.
    """
    if df_node.empty:
        return {
            "header_repetition_score": 0.0,
            "ua_score": 0.0,
            "fingerprint_score": 0.0,
            "top_header_signature": None,
            "top_ua": None,
            "unique_user_agents": 0,
        }

    if "header_order_signature" in df_node.columns:
        header_order_sigs = df_node["header_order_signature"]
    else:
        header_order_sigs = df_node["headers"].apply(
            lambda h: hashlib.sha256("|".join(h.keys()).encode("utf-8")).hexdigest()[:8]
        )

    sig_counts = header_order_sigs.value_counts(normalize=True)
    repetition_score = float(sig_counts.iloc[0]) if not sig_counts.empty else 0.0

    ua_counts = df_node["user_agent"].value_counts()
    ua_diversity = len(ua_counts) / max(len(df_node), 1)
    ua_score = 1.0 - ua_diversity

    top_ua = str(ua_counts.index[0]) if len(ua_counts) else ""

    return {
        "header_repetition_score": round(repetition_score, 4),
        "ua_score": round(float(ua_score), 4),
        "fingerprint_score": round(0.6 * repetition_score + 0.4 * ua_score, 4),
        "top_header_signature": str(sig_counts.index[0]) if not sig_counts.empty else None,
        "top_ua": top_ua,
        "unique_user_agents": int(len(ua_counts)),
    }
