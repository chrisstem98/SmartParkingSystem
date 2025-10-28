import os
from pathlib import Path
from ultralytics import YOLO

class YoloServiceDetector:
    #service to load and run YOLOv8 model for parking detection.
    
    _instance = None
    _model = None
    
    def __new__(cls, *args, **kwargs):
    # Singleton pattern to ensure only one instance of the model is loaded.
        if cls._instance is None:
            cls._instance = super(YoloServiceDetector, cls).__new__(cls)
        return cls._instance
    
    base_dir = Path(__file__).parent
    models_dir = base_dir.parent / 'models'
    #models_dir = parent_dir / 'models/best.pt'
    
    def __init__(self, model_path='models/best.pt'):
        #Load YOLO model only once
        if self._model is None:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
                print(f"Loading YOLO model from {model_path}...")  
            self._model = YOLO(model_path)
            
            
    def analyze_image(self, image_path: str):
        #Run YOLO inference on image and return results
        if self._model is None:
            raise ValueError("Model not loaded properly.")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found at {image_path}")
        
        #Run detection
        results = self._model.predict(source=image_path, conf=0.5, save=False)
        
        #Unitialize counts
        counts = {"empty": 0, "occupied": 0}
        
        #Process detections
        for result in results:
            for cls in result.boxes.cls:
                cls_name = self._model.names[int(cls)]
                counts[cls_name] = counts.get(cls_name, 0) + 1
        
        
        print(f"Detection results for {os.path.basename(image_path)}: {counts}")
        return counts
        