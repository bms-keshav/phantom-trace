from __future__ import annotations

from pathlib import Path


REQUIRED_PATHS = [
    "backend/main.py",
    "backend/parser.py",
    "backend/graph.py",
    "backend/scoring.py",
    "backend/fingerprint.py",
    "backend/beacon.py",
    "backend/dossier.py",
    "backend/sigma.py",
    "frontend/src/App.jsx",
    "frontend/src/components/NetworkGraph.jsx",
    "frontend/src/components/CommandNodePanel.jsx",
    "frontend/src/components/MetadataPanel.jsx",
    "frontend/src/components/KillChainTimeline.jsx",
    "frontend/src/components/ScoreRadar.jsx",
    "frontend/src/components/ThreatDossier.jsx",
    "data/generate_logs.py",
    "data/sample_logs.json",
    "data/field_map.json",
    "docs/architecture.md",
    "docs/submission_checklist.md",
    "README.md",
    "RUNNING.md",
    "requirements.txt",
    ".gitignore",
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    missing: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            missing.append(rel)

    print("== PHANTOM TRACE Submission Check ==")
    print("required_files:", len(REQUIRED_PATHS))
    print("missing_files:", len(missing))

    if missing:
        for item in missing:
            print(" -", item)
        raise SystemExit(1)

    readme = (root / "README.md").read_text(encoding="utf-8", errors="ignore")
    must_have = [
        "AI Usage Documentation",
        "Core Detection Formula",
        "API Endpoints",
    ]
    missing_sections = [s for s in must_have if s not in readme]

    if missing_sections:
        print("missing_readme_sections:", missing_sections)
        raise SystemExit(1)

    print("readme_sections: ok")
    print("status: SUBMISSION_STRUCTURE_READY")


if __name__ == "__main__":
    main()
