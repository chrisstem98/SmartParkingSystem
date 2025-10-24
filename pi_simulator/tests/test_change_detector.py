"""
------------------------------------------------------------
Test Script for the ChangeDetector (pixel diff method)
------------------------------------------------------------
Compares two consecutive images and prints whether
a change was detected + percentage of pixel difference.
------------------------------------------------------------
"""

import cv2
import numpy as np
import glob
import os
from pi_simulator.change_detector import ChangeDetector

# --- configuration ---
DATASET_PATH = "data/datasets/PKLot/valid/images"

# --- load two sample images ---
images = sorted(glob.glob(os.path.join(DATASET_PATH, "*.jpg")))

if len(images) < 2:
    raise SystemExit(" Need at least 2 images to test change detector.")

img1_path = images[0]
img2_path = images[1]

# --- visualize (optional) ---
print(f"Comparing:\n 1 {os.path.basename(img1_path)}\n 2️⃣ {os.path.basename(img2_path)}")


detector = ChangeDetector(threshold=0.9)
detector.prev_frame = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
new = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

diff = cv2.absdiff(new, detector.prev_frame)
non_zero = np.count_nonzero(diff)
ratio = non_zero / diff.size
changed = ratio > (1 - detector.threshold)

print("--------------------------------------------------")
print(f"Pixel difference ratio: {ratio:.4f}")
print(f"Threshold: {detector.threshold:.2f} → Change detected? {'YES' if changed else 'NO'}")
print("--------------------------------------------------")

# --- (optional) show diff image ---
cv2.imshow("Image 1", detector.prev_frame)
cv2.imshow("Image 2", new)
cv2.imshow("Difference", diff)
cv2.waitKey(0)
cv2.destroyAllWindows()
