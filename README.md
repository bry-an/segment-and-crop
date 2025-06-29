# Crop and Segment

## Description

Simple pipeline using LandingAI to run a segmentation inference locally then crop the image to the segmentation result.

## Usage

### Setup

First, set up the virtual environment and install dependencies:

```bash
make install
```

### Main Commands

#### Crop and Segment Images

Process images using the segmentation model:

```bash
make crop DATASET=train DATASET_NAME=dataset_v1 MODEL_VERSION=v1.0
```

**Parameters:**
- `DATASET`: Dataset type (e.g., train, test, val)
- `DATASET_NAME`: Name of the dataset
- `MODEL_VERSION`: Version of the segmentation model

### Docker Commands

#### Build Docker Image

Build the segmentation Docker image:

```bash
make docker-build-segment
```

#### Run Docker Container

Run the segmentation model service locally:

```bash
make docker-run-segment
```

The model service will be available at `http://localhost:8001`.