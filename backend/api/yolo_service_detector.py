import os
from ultralytics import YOLO

class YoloServiceDetector:
    """Loads YOLO once and provides detection with full box details."""

    _model = None

    def __init__(self, model_path):
        if YoloServiceDetector._model is None:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"YOLO model not found: {model_path}")
            YoloServiceDetector._model = YOLO(model_path)

    def analyze_image(self, image_path: str):
        """Run YOLO model, return counts, detections, annotated image path"""
        results = YoloServiceDetector._model.predict(
            source=image_path,
            conf=0.5,
            save=True,              # save annotated image
            project="runs/backend", # temp dir
            name="annotated",
            exist_ok=True
        )

        result = results[0]

        # Annotated image location:
        annotated_path = result.save_dir + "/" + os.path.basename(image_path)

        counts = {"empty": 0, "occupied": 0}
        detections = []

        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = YoloServiceDetector._model.names[cls_id]
            conf = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            w = int(x2 - x1)
            h = int(y2 - y1)
            cx = int(x1 + w / 2)
            cy = int(y1 + h / 2)

            detections.append({
                "cls_name": cls_name,
                "confidence": conf,
                "x": cx,
                "y": cy,
                "w": w,
                "h": h,
            })

            counts[cls_name] += 1

        return {
            "counts": counts,
            "detections": detections,
            "annotated_path": annotated_path,
        }
# End of backend/api/yolo_service_detector.py