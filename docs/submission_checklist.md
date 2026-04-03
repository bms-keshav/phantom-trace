# Submission Checklist

## Core Deliverables

- [x] Interactive Network Attack Graph
- [x] Command Node Detection with confidence scores
- [x] Metadata Pattern Analysis (headers + user-agent + timing)

## Technical Differentiators

- [x] FFT-based beaconing score
- [x] Deterministic composite scoring formula
- [x] SIGMA rule generation
- [x] PDF threat dossier generation
- [x] Kill-chain timeline scrubber

## Engineering Quality

- [x] Modular backend architecture
- [x] Frontend componentized layout
- [x] Session-isolated analysis storage (`analysis_id` keyed)
- [x] Non-blocking analysis route (heavy compute offloaded from event loop)
- [x] Graph/scoring performance optimizations for larger datasets
- [x] Parser supports JSON/NDJSON/CSV
- [x] Field mapping config for event-day schema drift
- [x] Sample synthetic dataset with embedded ground truth

## Demo Readiness

- [x] 3-minute demo flow documented
- [x] Quick run instructions documented
- [x] Smoke test script available

## Compliance

- [x] AI usage documentation in README
- [x] No training-based ML dependency required
- [x] Reproducible deterministic outputs
