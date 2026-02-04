# For running the Pi Simulator for demo purposes. Each run for a specific Pi device. 

#set PI_SITE=UFPR04
#set PI_ID=pi-ufpr04-001
#set BACKEND_URL=http://localhost:8000/api/upload-image/
#set DATASET_PATH=C:\SmartParking\datasets\UFPR04\images
#set INTERVAL_SECONDS=5
#set CHANGE_THRESHOLD=0.90
#python -m pi_simulator.main

#$env:PI_SITE="UFPR04"; $env:PI_ID="pi-ufpr04-001"; $env:BACKEND_URL="http://localhost:8000/api/upload-image/"; $env:DATASET_PATH=".\pi_simulator\UFPR04\images"; $env:INTERVAL_SECONDS="5"; $env:CHANGE_THRESHOLD="0.90"; python -m pi_simulator.main


import time
from pi_simulator.camera_handler import CameraHandler
from pi_simulator.change_detector import ChangeDetector
from pi_simulator.uploader import Uploader
from pi_simulator.config import (
    DATASET_PATH,
    INTERVAL_SECONDS,
    CHANGE_THRESHOLD,
    BACKEND_URL,
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    PI_SITE,
    PI_ID,
)
from pi_simulator.utils.logger import setup_logger


class PiSimulator:
    def __init__(self):
        self.logger = setup_logger(f"PiSimulator[{PI_ID}|{PI_SITE}]")

        self.camera = CameraHandler(DATASET_PATH)
        self.detector = ChangeDetector(threshold=CHANGE_THRESHOLD)

        self.uploader = Uploader(
            backend_url=BACKEND_URL,
            minio_endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            bucket_name=MINIO_BUCKET,
            site_code=PI_SITE,
            pi_id=PI_ID,
        )

    def run(self):
        self.logger.info("Starting Pi Simulator loop")

        while True:
            try:
                frame_path = self.camera.get_next_frame()
                self.logger.info(f"Captured frame: {frame_path}")

                if self.detector.has_changed(frame_path):
                    self.logger.info("Change detected → uploading to backend")

                    response = self.uploader.upload_to_backend(frame_path)
                    self.logger.info(f"Backend response: {response}")
                else:
                    self.logger.info("No significant change detected")

                time.sleep(INTERVAL_SECONDS)

            except Exception as e:
                self.logger.error(f"Simulator error: {e}")
                time.sleep(5)


if __name__ == "__main__":
    PiSimulator().run()
