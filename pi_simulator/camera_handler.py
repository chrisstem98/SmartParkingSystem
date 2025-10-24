import os
import glob


class CameraHandler:

    # Handles image retrieval from a dataset of images stored in a specified directory. Need Improvement.
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.images = sorted(glob.glob(os.path.join(dataset_path, "*.jpg")))
        self.index = 0

    def get_next_frame(self):
        # Returns the next image path from the dataset in a cyclic manner.(simulated camera frame)
        if not self.images:
            raise FileNotFoundError("No images found in the dataset path.")
        
        image_path = self.images[self.index]
        self.index = (self.index + 1) % len(self.images)
        return image_path
