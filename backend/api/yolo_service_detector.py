from ultralytics import YOLO
from PIL import Image
import os

class YoloServiceDetector:
    _instance = None
    _model = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_path='models/best.pt'):
        if self._model is None:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            self._model = YOLO(model_path)

    def analyze_image(self, image_path: str):
        """
        Run YOLO detection on an image and return:
        - counts of classes
        - list of detections
        - path to annotated image
        """
        # Run YOLO inference
        results = self._model.predict(source=image_path, conf=0.5, save=False)

        # Get image size
        with Image.open(image_path) as im:
            img_w, img_h = im.size

        counts = {"empty": 0, "occupied": 0}
        detections = []

        for r in results:
            names = r.names
            if not r.boxes:
                continue

            for b in r.boxes:
                cls_id = int(b.cls.item())
                cls_name = names.get(cls_id, str(cls_id))
                conf = float(b.conf.item())
                x1, y1, x2, y2 = b.xyxy[0].tolist()
                cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
                w, h = (x2 - x1), (y2 - y1)

                detections.append({
                    "cls_name": cls_name,
                    "conf": conf,
                    "cx_norm": cx / img_w,
                    "cy_norm": cy / img_h,
                    "w_norm": w / img_w,
                    "h_norm": h / img_h,
                })

                if cls_name in counts:
                    counts[cls_name] += 1

        # ✅ Create annotated image using Ultralytics built-in plotting
        # (each result has a method `plot()` that returns an annotated image as a numpy array)
        annotated_image = results[0].plot()  # first result annotated frame
        annotated_filename = f"detected_{os.path.basename(image_path)}"

        # Save annotated image under temp/
        annotated_path = os.path.join(os.path.dirname(image_path), annotated_filename)
        Image.fromarray(annotated_image).save(annotated_path)

        return {
            "counts": counts,
            "detections": detections,
            "annotated_path": annotated_path,
            "image_size": {"w": img_w, "h": img_h},
        }
