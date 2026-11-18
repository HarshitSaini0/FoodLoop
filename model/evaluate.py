"""Evaluate on the held-out test folder and write docs/results.md.

    python model/evaluate.py --data data/images/test

Key safety numbers:
  false-safe rate   = rotten predicted fresh / all rotten   (the dangerous error)
  false-reject rate = fresh predicted rotten / all fresh     (wasted good food)
Also reports how many images the router would send to "hold" at the 0.80 confidence floor.
"""
import argparse
import io
from pathlib import Path

from PIL import Image

from foodloop import classifier
from foodloop.router import CONFIDENCE_MIN

EXT = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/images/test")
    ap.add_argument("--out", default="docs/results.md")
    a = ap.parse_args()

    tp = {"fresh": {"fresh": 0, "rotten": 0}, "rotten": {"fresh": 0, "rotten": 0}}
    held = total = 0
    backend = None
    for truth in ("fresh", "rotten"):
        for p in sorted((Path(a.data) / truth).glob("*")):
            if p.suffix.lower() not in EXT:
                continue
            buf = io.BytesIO()
            Image.open(p).convert("RGB").save(buf, "JPEG")
            r = classifier.predict(buf.getvalue())
            backend = r["classifier"]
            tp[truth][r["label"]] += 1
            total += 1
            held += r["confidence"] < CONFIDENCE_MIN
    if not total:
        raise SystemExit("No test images found")

    nf, nr = sum(tp["fresh"].values()), sum(tp["rotten"].values())
    acc = (tp["fresh"]["fresh"] + tp["rotten"]["rotten"]) / total
    fs = tp["rotten"]["fresh"] / nr if nr else float("nan")
    fr = tp["fresh"]["rotten"] / nf if nf else float("nan")
    md = f"""# Results

Classifier backend: `{backend}`. Test images: {total} ({nf} fresh, {nr} rotten). Held-out, not used in training.

| | Predicted fresh | Predicted rotten |
|---|---|---|
| **Actually fresh** | {tp['fresh']['fresh']} | {tp['fresh']['rotten']} |
| **Actually rotten** | {tp['rotten']['fresh']} | {tp['rotten']['rotten']} |

- Accuracy: {acc:.1%}
- **False-safe rate** (rotten predicted fresh): {fs:.1%}
- False-reject rate (fresh predicted rotten): {fr:.1%}
- Sent to hold by the {CONFIDENCE_MIN:.2f} confidence floor: {held} of {total} ({held / total:.1%})

Public-dataset photos only. This is not a food-safety validation.
"""
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(md)
    print(md)


if __name__ == "__main__":
    main()
