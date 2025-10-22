from pathlib import Path 
import cv2

class CameraHandler:
    def __init__(self, camera_index=0, save_directory="captured_images"):
        self.camera_index = camera_index
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.camera = cv2.VideoCapture(self.camera_index)

    def capture_image(self, filename="image.jpg"):
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError("Failed to capture image from camera.")
        
        image_path = self.save_directory / filename
        cv2.imwrite(str(image_path), frame)
        return image_path

    def release(self):
        self.camera.release()



