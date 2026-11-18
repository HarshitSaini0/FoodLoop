"""Train a fresh-vs-rotten classifier (MobileNetV3-small transfer learning).

Expected folders (ImageFolder layout, class names must be exactly "fresh" and "rotten"):
    data/images/train/{fresh,rotten}/*.jpg
    data/images/val/{fresh,rotten}/*.jpg
    data/images/test/{fresh,rotten}/*.jpg   (never used for training; used by evaluate.py)

Run (Colab GPU is fine, a laptop CPU also works for a small dataset):
    pip install torch torchvision
    python model/train.py --data data/images --epochs 5
Writes model/model.pt with {"state_dict": ..., "classes": [...]}.
"""
import argparse
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]


def loaders(root: Path, batch: int):
    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    eval_tf = transforms.Compose([
        transforms.Resize(256), transforms.CenterCrop(224),
        transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    tr = datasets.ImageFolder(root / "train", train_tf)
    va = datasets.ImageFolder(root / "val", eval_tf)
    return (tr, DataLoader(tr, batch, shuffle=True, num_workers=2),
            DataLoader(va, batch, num_workers=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/images")
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--out", default="model/model.pt")
    a = ap.parse_args()

    torch.manual_seed(0)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    ds, tr, va = loaders(Path(a.data), a.batch)
    if sorted(ds.classes) != ["fresh", "rotten"]:
        raise SystemExit(f"Class folders must be 'fresh' and 'rotten', found {ds.classes}")

    net = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    net.classifier[-1] = nn.Linear(net.classifier[-1].in_features, len(ds.classes))
    net.to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    best = 0.0
    for ep in range(a.epochs):
        net.train()
        for x, y in tr:
            x, y = x.to(dev), y.to(dev)
            opt.zero_grad()
            loss_fn(net(x), y).backward()
            opt.step()
        net.eval()
        ok = n = 0
        with torch.no_grad():
            for x, y in va:
                ok += (net(x.to(dev)).argmax(1).cpu() == y).sum().item()
                n += len(y)
        acc = ok / max(n, 1)
        print(f"epoch {ep + 1}/{a.epochs}  val accuracy {acc:.3f}")
        if acc >= best:
            best = acc
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            torch.save({"state_dict": net.cpu().state_dict(), "classes": ds.classes}, a.out)
            net.to(dev)
    print(f"saved best model to {a.out} (val accuracy {best:.3f})")


if __name__ == "__main__":
    main()
