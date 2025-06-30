# Example usage:
#   make crop DATASET=train DATASET_NAME=dataset_v1 MODEL_VERSION=v1.0

PY = .venv/bin/python

venv:
	python -m venv .venv && .venv/bin/pip install -U pip

install: venv
	.venv/bin/pip install -r requirements.txt

crop:
	$(PY) src/crop_and_segment.py --dataset $(DATASET) --dataset-name $(DATASET_NAME) --model-version $(MODEL_VERSION)

# Basic dedupe with default settings
dedupe:
	$(PY) src/dedupe.py data/combined --threshold 10 --move-duplicates data/dupes

# Aggressive dedupe (lower threshold = more strict)
dedupe-strict:
	$(PY) src/dedupe.py data/combined --threshold 5 --move-duplicates data/dupes

# Loose dedupe (higher threshold = more lenient)
dedupe-loose:
	$(PY) src/dedupe.py data/combined --threshold 20 --move-duplicates data/dupes

# Just report duplicates without moving them
dedupe-report:
	$(PY) src/dedupe.py data/combined --threshold 10

manifest:
	$(PY) src/split_manifest.py

# ---- Docker image names
SEGMENT_IMG   = segment

# ---- Build images ------------------------------------------
docker-build-segment:
	docker build --build-arg MODEL_ZIP=segment.zip \
	             -t $(SEGMENT_IMG) .

# ---- Run containers locally --------------------------------
docker-run-segment: docker-build-segment
	docker run --rm -p 8001:8000 $(SEGMENT_IMG)