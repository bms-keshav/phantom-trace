# PHANTOM TRACE Architecture

PHANTOM TRACE is a deterministic cyber forensic attribution system composed of:

1. Data Ingestion Layer (`backend/parser.py`)
2. Attack Graph Layer (`backend/graph.py`)
3. Attribution Engine (`backend/beacon.py`, `backend/fingerprint.py`, `backend/scoring.py`)
4. Operational Outputs (`backend/sigma.py`, `backend/dossier.py`)
5. API Layer (`backend/main.py`)
6. Investigation UI (`frontend/src/*`)

The design prioritizes explainability over black-box ML so analysts can audit why a node is flagged.
