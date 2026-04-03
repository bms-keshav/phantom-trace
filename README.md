# PHANTOM TRACE

PHANTOM TRACE is a cyber forensic attribution investigation system designed to identify hidden command-and-control behavior in noisy API traffic.

It uses deterministic scoring (graph centrality + timing beaconing + metadata fingerprinting) so every decision is explainable under hackathon judging.

## Stack

- Backend: Python 3.11+, FastAPI, NetworkX, Pandas, NumPy, SciPy
- Frontend: React (Vite), TailwindCSS, react-force-graph-2d, Recharts
- Outputs: SIGMA rule, PDF threat dossier (ReportLab)

## Repository Structure

```text
phantom-trace/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── parser.py
│   ├── graph.py
│   ├── scoring.py
│   ├── fingerprint.py
│   ├── beacon.py
│   ├── dossier.py
│   └── sigma.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── styles.css
│   │   └── components/
│   │       ├── NetworkGraph.jsx
│   │       ├── CommandNodePanel.jsx
│   │       ├── MetadataPanel.jsx
│   │       ├── KillChainTimeline.jsx
│   │       ├── ScoreRadar.jsx
│   │       └── ThreatDossier.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js
├── data/
│   ├── generate_logs.py
│   ├── sample_logs.json
│   └── field_map.json
├── docs/
│   └── architecture.md
├── README.md
└── requirements.txt
```

## Core Detection Formula

Attribution score is deterministic:

C = 0.20 * centrality + 0.40 * beacon + 0.30 * fingerprint + 0.10 * coordination

Where:

- `centrality`: weighted normalized graph influence score
- `beacon`: periodicity score using IAT variance + FFT spectral ratio
- `fingerprint`: header ordering repetition + user-agent anomaly
- `coordination`: proportion of graph neighbors contacted by node

## Data Ingestion Modes

`backend/parser.py` supports:

- JSON array of objects
- NDJSON (one JSON object per line)
- CSV with auto-detected delimiter

Field aliases are configurable via `data/field_map.json`.

## Quick Start

### 1) Backend setup

```bash
cd phantom-trace
python -m venv .venv
# activate venv
pip install -r requirements.txt
```

If your local Python resolver fails on pinned versions, install these without pins:

```bash
pip install fastapi uvicorn[standard] pandas numpy scipy networkx python-multipart reportlab
```

### 2) Generate sample logs

```bash
python data/generate_logs.py
```

This creates `data/sample_logs.json` with 5000 requests and an injected hidden C2 node (`10.4.2.11`) beaconing roughly every 12 seconds.

### 3) Run backend API

```bash
uvicorn backend.main:app --reload
```

### 4) Run frontend

```bash
cd frontend
npm install
npm run dev
```

Then open the Vite URL (typically `http://localhost:5173`), upload `data/sample_logs.json`, and investigate.

## API Endpoints

- `GET /api/health`
- `POST /api/analyze` (multipart upload)
- `GET /api/node/{ip}/sigma`
- `GET /api/node/{ip}/dossier`

## Demo Flow (3 minutes)

1. Upload logs and show network graph explosion.
2. Scrub timeline from 0% to 100% to reveal kill-chain progression.
3. Click top-ranked node and explain radar breakdown.
4. Highlight beacon dominant period and metadata fingerprint repetition.
5. Export SIGMA rule and PDF dossier.

## AI Usage Documentation

AI tools were used in the following ways:

1. **Explanation generation** (UI feature): The "Why this node?" explanation panel
	uses an LLM prompt to translate the numeric score breakdown into a plain-English
	forensic summary. The underlying detection is entirely deterministic - AI only
	translates the output, it does not influence the detection logic.

2. **Code assistance**: Used for boilerplate generation (FastAPI routes, React
	component scaffolding). All core algorithms (FFT beaconing, scoring formula,
	fingerprinting) were written and validated manually.

3. **Synthetic data generation**: Used to generate realistic network log patterns
	including the injected C2 node behavioral profile.

Architecture decision: we deliberately chose deterministic math over ML models
because explainability is a first-class requirement in threat attribution.
A judge or analyst must be able to understand why a node was flagged without
trusting a black box.
