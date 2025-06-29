"""
Run the local segmentation model (localhost:8001),
crop the largest detected rash in each image, and save the crops.

Requires:
  pip install landingai pillow
"""

from landingai.predict import EdgePredictor
from landingai.pipeline.frameset import Frame       # ← official Frame API
from pathlib import Path
import json
import argparse
from datetime import datetime

# ── Argument parsing ──────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Crop and segment rash images")
parser.add_argument("--dataset", choices=["train", "val", "test"], required=True,
                   help="Dataset split being processed")
parser.add_argument("--dataset-name", default="dataset_v1",
                   help="Name of the dataset")
parser.add_argument("--model-version", default="v1.0",
                   help="Model version being used")
args = parser.parse_args()

# ── Config ────────────────────────────────────────────────────────────────────
SEGMENTER_PORT = 8001                           # port where Docker model listens
INPUT_DIR      = Path("data/raw")               # source JPG/PNG photos
OUTPUT_DIR     = Path("data/cropped")           # where crops + metadata go
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

predictor = EdgePredictor(host="localhost", port=SEGMENTER_PORT)

metadata = []                                   # optional bookkeeping

# ── Run information ───────────────────────────────────────────────────────────
run_info = {
    "dataset": args.dataset,
    "dataset_name": args.dataset_name,
    "model_version": args.model_version,
    "timestamp": datetime.now().isoformat(),
    "segmentation_port": SEGMENTER_PORT,
    "input_dir": str(INPUT_DIR),
    "output_dir": str(OUTPUT_DIR)
}

# ── Main loop ─────────────────────────────────────────────────────────────────
for img_path in INPUT_DIR.glob("*.[jpJP][pnPN]g"):
    print(f"🖼  {img_path.name}")

    frame = Frame.from_image(str(img_path))          # Wrap a Pillow image
    frame.run_predict(predictor)                # → predictions stored on frame

    if not frame.predictions:                   # None found
        print("   ⚠️  no rash detected")
        # add this to metadata
        metadata.append({
            "source": str(img_path),
            "output": None,
            "bbox": None,
            "score": None,
            "num_predicted_pixels": None,
            "error": "no rash detected"
        })
        continue

    # Frame.crop_predictions() yields a *new* Frame for every prediction
    crop_frames = list(frame.crop_predictions())  # type: ignore # SDK helper
    
    # Debug: inspect the first prediction object
    if crop_frames:
        first_pred = crop_frames[0].predictions[0]
        print(f"   Debug: prediction type: {type(first_pred)}")
        print(f"   Debug: bboxes: {first_pred.bboxes}")
        print(f"   Debug: num_predicted_pixels: {first_pred.num_predicted_pixels}")
    
    # Choose the largest crop (by area of original bbox)
    largest_crop = max(
        crop_frames,
        key=lambda cf: cf.predictions[0].num_predicted_pixels           # use pixel count instead of area
    )

    # Save the cropped image
    out_path = OUTPUT_DIR / img_path.with_suffix("").name
    out_path = out_path.with_name(out_path.name + "_crop.jpg")
    largest_crop.save_image(out_path)                      # Frame method

    # Record useful metadata
    bbox = largest_crop.predictions[0].bboxes[0] if largest_crop.predictions[0].bboxes else None
    metadata.append({
        "source": str(img_path),
        "output": str(out_path),
        "bbox": bbox,
        "score": getattr(largest_crop.predictions[0], 'score', None),
        "num_predicted_pixels": largest_crop.predictions[0].num_predicted_pixels
    })

# Save metadata for downstream use
final_metadata = {
    "run_info": run_info,
    "crops": metadata,
    "summary": {
        "total_images_processed": len(list(INPUT_DIR.glob("*.[jpJP][pnPN]g"))),
        "successful_crops": len(metadata)
    }
}

(out_json := OUTPUT_DIR / "crop_metadata.json").write_text(
    json.dumps(final_metadata, indent=2)
)

print(f"\n✅ Cropped {len(metadata)} images → {OUTPUT_DIR}")
print(f"   Dataset: {args.dataset_name} ({args.dataset})")
print(f"   Model: {args.model_version}")
print(f"   Metadata saved to {out_json}")