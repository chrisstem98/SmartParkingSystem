import os
import requests
from urllib.parse import urlencode

from minio import Minio


class Uploader:
    def __init__(self, backend_url, minio_endpoint, access_key, secret_key, bucket_name, site_code, pi_id):
        self.backend_url = backend_url.rstrip("/") + "/"
        self.site_code = site_code
        self.pi_id = pi_id

        self.minio_endpoint = minio_endpoint
        self.bucket_name = bucket_name

        self.minio_client = Minio(
            minio_endpoint.replace("http://", "").replace("https://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=minio_endpoint.startswith("https://"),
        )

        # NOTE: bucket create stays here; if MinIO isn't running it may fail.
        # We'll keep it, but in our first tests we will not call upload_to_minio yet.

    def upload_to_backend(self, image_path: str):
        params = urlencode({"site": self.site_code})
        url = f"{self.backend_url}?{params}"

        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"device_id": self.pi_id}  # backend may ignore
            resp = requests.post(url, files=files, data=data, timeout=30)

        if resp.ok:
            return resp.json()
        return {"error": resp.text, "status_code": resp.status_code, "url": url}

    def upload_to_minio(self, image_path: str):
        filename = os.path.basename(image_path)
        object_name = f"{self.site_code}/{self.pi_id}/{filename}"

        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)

        self.minio_client.fput_object(self.bucket_name, object_name, image_path)
        return f"Uploaded {object_name} to MinIO bucket {self.bucket_name}"
