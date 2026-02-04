import os

PI_SITE = os.getenv("PI_SITE", "UFPR04")
PI_ID = os.getenv("PI_ID", f"pi-{PI_SITE.lower()}-001")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/upload-image/")

DATASET_PATH = os.getenv("DATASET_PATH", "data/datasets/PKLot/valid/images")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "10"))

CHANGE_THRESHOLD = float(os.getenv("CHANGE_THRESHOLD", "0.90"))

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "parking-images")
