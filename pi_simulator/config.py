# Configuration file for the Pi Simulator

BACKEND_URL = "http://localhost:8000/api/upload-image/"
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "parking-images"

DATASET_PATH = "data/datasets/PKLot/valid/images"
INTERVAL_SECONDS = 60  # interval between image uploads
