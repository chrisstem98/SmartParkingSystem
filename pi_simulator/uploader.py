import requests
import os
from minio import Minio

class Uploader:
    #   Uploads images to backend API and MinIO.

    def __init__(self, backend_url, minio_endpoint, access_key, secret_key, bucket_name):
        self.backend_url = backend_url
        self.minio_client = Minio(
            minio_endpoint.replace("http://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        self.bucket_name = bucket_name

        if not self.minio_client.bucket_exists(bucket_name):
            self.minio_client.make_bucket(bucket_name)

    def upload_to_backend(self, image_path: str):
        # Sends image to Django backend via HTTP POST.
        with open(image_path, "rb") as f:
            files = {"image": f}
            response = requests.post(self.backend_url, files=files)
        return response.json() if response.ok else {"error": response.text}

    def upload_to_minio(self, image_path: str):
        """Uploads image file to MinIO bucket."""
        filename = os.path.basename(image_path)
        self.minio_client.fput_object(self.bucket_name, filename, image_path)
        return f"Uploaded {filename} to MinIO bucket {self.bucket_name}"
