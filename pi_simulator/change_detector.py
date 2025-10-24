import cv2
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
    
        return ratio > 1 - self.threshold