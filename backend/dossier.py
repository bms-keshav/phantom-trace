from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_dossier_pdf(node_data: dict, sigma_rule: str, top_targets: list[str]) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50

    def line(text: str, step: int = 16, size: int = 10) -> None:
        nonlocal y
        c.setFont("Helvetica", size)
        c.drawString(40, y, text)
        y -= step

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "PHANTOM TRACE Threat Dossier")
    y -= 26

    c.setFont("Helvetica", 10)
    line(f"Analysis Time (UTC): {datetime.now(timezone.utc).isoformat()}")
    line(f"Node IP: {node_data.get('node')}")
    line(f"Final Score: {node_data.get('final_score')}")
    line(f"Confidence (%): {node_data.get('confidence_pct')}")
    line("Formula: C = 0.20*centrality + 0.40*beacon + 0.30*fingerprint + 0.10*coordination")
    y -= 8

    line("Score Breakdown:", size=12)
    bd = node_data.get("breakdown", {})
    line(f"  Centrality: {bd.get('centrality')}")
    line(f"  Beacon: {bd.get('beacon')}")
    line(f"  Fingerprint: {bd.get('fingerprint')}")
    line(f"  Coordination: {bd.get('coordination')}")

    y -= 8
    line("Beacon Analysis:", size=12)
    beacon = node_data.get("beacon_detail", {})
    line(f"  Dominant Period (sec): {beacon.get('dominant_period_sec')}")
    line(f"  IAT Std Dev: {beacon.get('iat_std')}")
    line(f"  Spectral Ratio: {beacon.get('spectral_ratio')}")

    y -= 8
    line("Fingerprint Analysis:", size=12)
    fp = node_data.get("fingerprint_detail", {})
    line(f"  Header Repetition: {fp.get('header_repetition_score')}")
    line(f"  Top Header Signature: {fp.get('top_header_signature')}")
    line(f"  Top User-Agent: {fp.get('top_ua')}")

    y -= 8
    line("Top 5 Targets:", size=12)
    for target in top_targets[:5]:
        line(f"  - {target}")

    y -= 12
    line("Generated SIGMA Rule:", size=12)
    c.setFont("Courier", 8)
    for raw in sigma_rule.splitlines()[:18]:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Courier", 8)
        c.drawString(40, y, raw[:110])
        y -= 10

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
