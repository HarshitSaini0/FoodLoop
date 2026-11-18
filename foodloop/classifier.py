"""Freshness classifier.

Two backends:
  * "mobilenet": a trained model at model/model.pt (made by model/train.py).
  * "demo-heuristic": a crude colour rule so the app runs before you train.
    It is a placeholder for demos and tests. It is NOT a real freshness model
    and must never be presented as one.
"""
import io
import os
from pathlib import Path

from PIL import Image

MODEL_PATH = Path(os.environ.get("FOODLOOP_MODEL", Path(__file__).resolve().parent.parent / "model" / "model.pt"))

_torch_bundle = None


def _load_torch_model():
    """Return (model, classes, transform) or None if torch/model are unavailable."""
    global _torch_bundle
    if _torch_bundle is not None:
        return _torch_bundle or None
    try:
        import torch
        from torchvision import models, transforms
        if not MODEL_PATH.exists():
            _torch_bundle = False
            return None
        ckpt = torch.load(MODEL_PATH, map_location="cpu")
        classes = ckpt["classes"]
        model = models.mobilenet_v3_small(weights=None, num_classes=len(classes))
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        tf = transforms.Compose([
            transforms.Resize((224, 224)), transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        _torch_bundle = (model, classes, tf)
    except Exception:
        _torch_bundle = False
        return None
    return _torch_bundle


def _heuristic(img: Image.Image) -> tuple[str, float]:
    small = img.convert("RGB").resize((64, 64))
    px = list(small.getdata())
    dark_or_brown = 0
    for r, g, b in px:
        bright = (r + g + b) / 3
        if bright < 70 or (r > g and r > b and r < 150 and g < 110):
            dark_or_brown += 1
    frac = dark_or_brown / len(px)
    label = "rotten" if frac > 0.35 else "fresh"
    confidence = min(0.90, 0.55 + abs(frac - 0.35))
    return label, round(confidence, 3)


def predict(image_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(image_bytes))
    img.load()
    bundle = _load_torch_model()
    if bundle:
        import torch
        model, classes, tf = bundle
        with torch.no_grad():
            probs = torch.softmax(model(tf(img.convert("RGB")).unsqueeze(0))[0], dim=0)
        idx = int(probs.argmax())
        return {"label": classes[idx], "confidence": round(float(probs[idx]), 3), "classifier": "mobilenet"}
    label, conf = _heuristic(img)
    return {"label": label, "confidence": conf, "classifier": "demo-heuristic"}
