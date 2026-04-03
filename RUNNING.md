# Running PHANTOM TRACE (Windows)

## 1) Backend

From project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

If pinned versions fail in your environment:

```powershell
pip install fastapi uvicorn[standard] pandas numpy scipy networkx python-multipart reportlab
```

Backend URL: http://127.0.0.1:8000

## 2) Frontend

In a new terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL: http://127.0.0.1:5173

## 3) Generate sample logs

```powershell
python data/generate_logs.py
```

Generated file: data/sample_logs.json

## 4) Quick API test

```powershell
python scripts/smoke_test.py
```

## 5) Demo flow

1. Upload `data/sample_logs.json`
2. Show top command-node confidence
3. Scrub timeline from 0 to 100
4. Click top node and explain radar + metadata
5. Export SIGMA and PDF
