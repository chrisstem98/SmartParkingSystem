import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


class ChangeDetector:
    """Detects structural changes between consecutive frames using SSIM."""

    def __init__(self, threshold: float = 0.90):
        """
        :param threshold: minimum SSIM similarity (0–1).
                          Lower = more sensitive, Higher = less sensitive.
        """
        self.threshold = threshold
        self.prev_frame = None

    def has_changed(self, new_frame_path: str) -> bool:
        """
        Compare new image to previous one using SSIM (Structural Similarity Index).
        Returns True if there is a significant change in the scene.
        """
        # Load image and convert to grayscale
        new = cv2.imread(new_frame_path, cv2.IMREAD_GRAYSCALE)
        if new is None:
            raise FileNotFoundError(f"Cannot read image: {new_frame_path}")

        # First frame → always treat as change
        if self.prev_frame is None:
            self.prev_frame = new
            return True

        # Ensure same size
        if new.shape != self.prev_frame.shape:
            new = cv2.resize(new, (self.prev_frame.shape[1], self.prev_frame.shape[0]))

        # Compute SSIM
        score, _ = ssim(new, self.prev_frame, full=True)

        # Change detected if similarity is below threshold
        has_change = score < self.threshold

        # Update previous frame
        self.prev_frame = new

        return has_change

#----------------OLD VERSION----------------
'''import cv2
import numpy as np


class ChangeDetector:
    #Detects changes between consecutive frames using background subtraction.
    
    def __init__(self, threshold = 0.95):
        self.threshold = threshold
        self.previous_frame = None
        
        
    def detect_change(self, new_frame):
        #Compares the new frame with the previous frame to detect significant changes.
        if self.previous_frame is None:
            self.previous_frame = new_frame
            return True
        
        
        diff = cv2.absdiff(self.previous_frame, new_frame)
        non_zero = np.count_nonzero(diff)
        ratio = non_zero / diff.size
        
        self.previous_frame = new_frame
    
        return ratio > 1 - self.threshold'''