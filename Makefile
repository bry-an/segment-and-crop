# Example usage:
#   make crop DATASET=train DATASET_NAME=dataset_v1 MODEL_VERSION=v1.0

PY = .venv/bin/python

venv:
	python -m venv .venv && .venv/bin/pip install -U pip

install: venv
	.venv/bin/pip install -r requirements.txt

crop:
	$(PY) src/crop_and_segment.py --dataset $(DATASET) --dataset-name $(DATASET_NAME) --model-version $(MODEL_VERSION)

dedupe:
	$(PY) src/dedupe.py data/cropped --move-duplicates data/cropped/dupes

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