import os
from ultralytics import YOLO
from django.conf import settings 

class YoloServiceDetector:
    _instance = None
    _model = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(YoloServiceDetector, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_path):
        if self._model is None:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model not found at {model_path}")
            self._model = YOLO(model_path)

    def analyze_image(self, image_path: str):
        """Run YOLO detection, save result image, and return class counts."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        #  Run inference
        results = self._model.predict(
            source=image_path,
            conf=0.5,
            save=False,   # we'll handle saving manually
            show=False
        )

        #  Prepare folder for saving annotated results
        results_dir = os.path.join(settings.MEDIA_ROOT, "results")
        os.makedirs(results_dir, exist_ok=True)

        # Save the annotated image
        result_img_path = os.path.join(results_dir, f"detected_{os.path.basename(image_path)}")
        for r in results:
            r.save(filename=result_img_path)

        # Count detections per class
        counts = {"empty": 0, "occupied": 0}
        for r in results:
            r.save(filename=result_img_path)
            for cls in r.boxes.cls:
                cls_name = self._model.names[int(cls)]
                counts[cls_name] = counts.get(cls_name, 0) + 1

        # Return both counts and result image path
        return {
            "counts": counts,
            "annotated_path": result_img_path
        }
