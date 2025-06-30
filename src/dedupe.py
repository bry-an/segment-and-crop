#!/usr/bin/env python3
"""
dedupe.py
Usage:
    python dedupe.py /path/to/img_dir1 /path/to/img_dir2 ... \
        --threshold 10 --move-duplicates /path/to/dupes
"""

import argparse, shutil, sys
from pathlib import Path
from tqdm import tqdm
from PIL import Image, UnidentifiedImageError
import imagehash

def phash(path, hash_size=16):
    """Return perceptual hash for an image file."""
    with Image.open(path) as img:
        return imagehash.phash(img, hash_size=hash_size)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("dirs", nargs="+", type=Path,
                   help="Image folders to scan (recursively)")
    p.add_argument("--threshold", "-t", type=int, default=10,
                   help="Hamming distance ≤ this = duplicate (default 10)")
    p.add_argument("--move-duplicates", "-m", type=Path,
                   help="If set, move duplicates into this folder")
    args = p.parse_args()

    # Mapping: hash → first path encountered
    canonical = {}
    duplicates = []

    img_paths = [p for d in args.dirs for p in d.rglob("*")
                 if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".gif"}]

    for path in tqdm(img_paths, desc="Hashing"):
        try:
            h = phash(path)
        except (UnidentifiedImageError, OSError):
            tqdm.write(f"⚠️ Skipping non-image: {path}")
            continue

        # Compare to existing hashes
        dup_found = False
        for ref_hash, ref_path in canonical.items():
            if h - ref_hash <= args.threshold:       # Hamming distance
                duplicates.append((path, ref_path, h - ref_hash))
                dup_found = True
                break

        if not dup_found:
            canonical[h] = path  # new unique image

    # Report / move duplicates
    if duplicates:
        print(f"\nFound {len(duplicates)} potential duplicates "
              f"(threshold ≤ {args.threshold}):")
        for dup, orig, dist in duplicates:
            print(f"[d={dist:2}] {dup}  →  {orig}")

        if args.move_duplicates:
            dup_dir = args.move_duplicates
            dup_dir.mkdir(parents=True, exist_ok=True)
            for dup, _, _ in duplicates:
                target = dup_dir / dup.name
                shutil.move(str(dup), target)
            print(f"\nMoved {len(duplicates)} files to {dup_dir}")
    else:
        print("✅ No duplicates detected!")

if __name__ == "__main__":
    sys.exit(main())