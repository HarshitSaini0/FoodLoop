# FoodLoop

A prototype that spots food about to spoil and proposes where it should go, with a person always making the final call and a tamper-evident record of who did what.

Built after the idea took 1st place at the UFV Community Ideation Jam 2026 (Future Ready Communities theme).

> **Status: prototype.** The vision model is trained on public photos and has not been validated for food safety. The demo credit has no monetary value. Do not use this to decide whether real food is safe to eat or donate.

## The loop

```
photo -> model proposes label + route -> HUMAN review (confirm or override)
      -> donor confirms handover -> recipient confirms receipt -> credit written to ledger
```

Routes follow the EPA Food Recovery Hierarchy: people, then animals, then energy or compost. Anything uncertain goes to **hold**.

## What is in here

| Part | File | What it does |
|---|---|---|
| Vision model | `model/train.py`, `foodloop/classifier.py` | MobileNetV3-small, fresh vs rotten. Falls back to a labelled demo heuristic if no trained model exists. |
| Rule engine | `foodloop/router.py` | Deterministic routing. No LLM decides. Higher-risk food (meat, dairy, ready-to-eat) and confidence below 0.80 always go to hold. |
| Review app | `foodloop/app.py` | FastAPI: upload, review, handover confirmations, batch list. |
| Ledger | `foodloop/ledger.py` | Append-only SQLite with a SHA-256 hash chain. Credit is issued only after human review, donor confirmation and recipient confirmation by two different parties. |
| Evaluation | `model/evaluate.py` | Confusion matrix, **false-safe rate** (rotten predicted fresh), false-reject rate. |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                                  # 12 tests
uvicorn foodloop.app:app --reload       # http://127.0.0.1:8000
```

Without a trained model the app uses a crude colour heuristic and says so on every result (`demo-heuristic`). It exists only so the workflow can be demonstrated.

## Train a real model

1. Download a public fresh-vs-rotten fruit/vegetable image dataset (for example from Kaggle). **Check its licence** and do not commit the images.
2. Arrange it as `data/images/{train,val,test}/{fresh,rotten}/`. Keep the test split untouched.
3. Train and evaluate:
   ```bash
   pip install -r requirements-train.txt
   python model/train.py --data data/images --epochs 5
   python model/evaluate.py --data data/images/test
   ```
   Free Colab GPU works. `model/model.pt` is picked up automatically (or set `FOODLOOP_MODEL`).
4. Paste the numbers from `docs/results.md` into the table below.

## Results

| Metric | Value |
|---|---|
| Dataset / size | _fill in_ |
| Accuracy | _fill in_ |
| False-safe rate (the one that matters) | _fill in_ |
| False-reject rate | _fill in_ |
| Share sent to hold | _fill in_ |

## Limitations

- Trained on public photos taken in good light; real farms, bins and stores look different.
- A photo cannot show pathogens, mould inside, or temperature history. It is a triage aid, not a safety check.
- Higher-risk categories are always held for a person.
- The ledger proves records were not edited after the fact; it does not prove that the events happened.
- Single-node SQLite, demo data only, no real user accounts.

## Docs

- [Architecture](docs/ARCHITECTURE.md): diagrams, data flow, ledger rules, design decisions
- [Limitations and numbers](docs/LIMITATIONS.md): why it is not accurate, sourced statistics, wording guide
- [Pitch sheet](docs/PITCH.md): talking points, demo script, tough questions
- [Brand guide](docs/BRAND.md): archetype, voice, colours

## Deploy

See [docs/DEPLOY.md](docs/DEPLOY.md) for Oracle Cloud (systemd, Apache reverse proxy, DuckDNS, HTTPS, password).
