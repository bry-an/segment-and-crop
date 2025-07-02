#!/usr/bin/env python3
"""
build_manifest.py  –  create LandingLens-ready manifest.csv

Assumes directory structure:
combined_images/
    ├── Positive/   (1005 *.jpg | *.png ...)
    └── Negative/   ( 995 ...)

Usage:
  python build_manifest.py --root combined_images --out manifest.csv
"""
import argparse, csv, random
from pathlib import Path
from collections import defaultdict
from sklearn.model_selection import StratifiedShuffleSplit

def collect_images(root: Path):
    """Return list of (relative_path, label, origin) tuples."""
    images, labels, origins = [], [], []
    for label_dir in ("Positive", "Negative"):
        folder = root / label_dir
        if not folder.exists():
            raise FileNotFoundError(f"Expected {folder}")
        for img_path in folder.rglob("*.[jpJP][pnPN]g"):
            rel = img_path.relative_to(root)
            images.append(str(rel))
            labels.append("EM" if label_dir == "Positive" else "Not-EM")
            origins.append("curated")
    return images, labels, origins

def stratified_split(y, test_size=0.1, val_size=0.2, seed=42):
    """Return list of splits: train/dev/test."""
    # First split off test (10 %)
    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_val_idx, test_idx = next(sss1.split(X=[0]*len(y), y=y))
    # Now split train_val into train & dev
    y_train_val = [y[i] for i in train_val_idx]
    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=val_size/(1-test_size), random_state=seed)
    train_idx, dev_idx = next(sss2.split(X=[0]*len(y_train_val), y=y_train_val))
    # Map local indices back to global
    train = [train_val_idx[i] for i in train_idx]
    dev   = [train_val_idx[i] for i in dev_idx]
    return train, dev, test_idx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path, help="combined_images/ folder")
    ap.add_argument("--out", default="manifest.csv", type=Path)
    args = ap.parse_args()

    images, labels, origins = collect_images(args.root)
    train_idx, dev_idx, test_idx = stratified_split(labels)

    split_map = {i: "train" for i in train_idx}
    split_map.update({i: "dev"   for i in dev_idx})
    split_map.update({i: "test"  for i in test_idx})

    with args.out.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "label", "split", "origin"])
        for i, (fp, lbl, org) in enumerate(zip(images, labels, origins)):
            writer.writerow([fp, lbl, split_map[i], org])

    print(f"✅ Wrote {len(images)} rows to {args.out}")
    counts = defaultdict(int)
    for sp in split_map.values(): counts[sp] += 1
    print("Split counts:", dict(counts))

if __name__ == "__main__":
    main()