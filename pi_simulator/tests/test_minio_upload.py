"""
------------------------------------------------------------
Test Script for MinIO Upload (Standalone)
------------------------------------------------------------
Uploads 3 sample images from dataset to MinIO bucket.
Verifies that connection and uploads work correctly.
------------------------------------------------------------
"""

import glob
import os
from pi_simulator.uploader import Uploader
from pi_simulator.config import *

# --- Load 3 sample images ---
images = sorted(glob.glob(os.path.join(DATASET_PATH, "*.jpg")))[:3]
if not images:
    raise SystemExit(" No images found in dataset path.")

print(f" Found {len(images)} images for upload test:")

for img in images:
    print(" -", os.path.basename(img))

# --- Initialize uploader ---
uploader = Uploader(
    BACKEND_URL,
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET
)

# --- Upload each image to MinIO ---
print("\n Uploading to MinIO...\n")

for img_path in images:
    try:
        result = uploader.upload_to_minio(img_path)
        print(f"{os.path.basename(img_path)} → {result}")
    except Exception as e:
        print(f"Failed to upload {os.path.basename(img_path)}: {e}")

print("\n Done! Check your MinIO bucket to verify uploads.")
