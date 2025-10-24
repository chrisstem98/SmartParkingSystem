import time
from pi_simulator.camera_handler import CameraHandler
from pi_simulator.change_detector import ChangeDetector
from pi_simulator.uploader import Uploader
from pi_simulator.config import *
from pi_simulator.utils.logger import setup_logger

class PiSimulator:
    """Main orchestrator for the Raspberry Pi simulation."""

    def __init__(self):
        self.logger = setup_logger("PiSimulator")
        self.camera = CameraHandler(DATASET_PATH)
        self.detector = ChangeDetector(threshold=0.9)
        self.uploader = Uploader(
            BACKEND_URL,
            MINIO_ENDPOINT,
            MINIO_ACCESS_KEY,
            MINIO_SECRET_KEY,
            MINIO_BUCKET
        )

    def run(self):
        """Continuously simulate image capture and upload."""
        self.logger.info("Starting Pi Simulator loop...")
        while True:
            try:
                frame = self.camera.get_next_frame()
                self.logger.info(f"Captured image: {frame}")

                if self.detector.has_changed(frame):
                    self.logger.info("Change detected! Uploading image...")
                    minio_res = self.uploader.upload_to_minio(frame)
                    #AS place holder for now backend_res = self.uploader.upload_to_backend(frame)
                    self.logger.info(f"MinIO: {minio_res}")
                    #self.logger.info(f"Backend response: {backend_res}")
                else:
                    self.logger.info("No significant change detected.")

                self.logger.info(f"Sleeping for {INTERVAL_SECONDS} seconds...\n")
                time.sleep(INTERVAL_SECONDS)

            except KeyboardInterrupt:
                self.logger.info("Simulation stopped manually.")
                break
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                time.sleep(5)

if __name__ == "__main__":
    simulator = PiSimulator()
    simulator.run()