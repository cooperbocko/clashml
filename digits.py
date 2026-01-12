from ultralytics import YOLO
from PIL import Image

from roboflow import Roboflow

class DetectDigits:
    def __init__(self, is_roboflow: bool, model_path: str, env_path: str):
        self.is_roboflow = is_roboflow
        self.yolo = YOLO(model_path)
        self.roboflow = Roboflow('clash-digit-detection-zjhdw/5', env_path)
        
    def predict(self, image: Image) -> str:
        image = Roboflow.preprocess_image(image)
        digits = ''
        if self.is_roboflow:
            results = self.roboflow.predict(image)
            if results != None:
                sorted_predictions = sorted(results, key=lambda r: r['x'])
                for prediction in sorted_predictions:
                    digits = digits + prediction['class']
        else:
            results = self.yolo.predict(source=image, verbose=False)[0]
            boxes = results.boxes.xyxy.cpu().numpy()
            labels = [results.names[int(i)] for i in results.boxes.cls]
            sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
            digits = ''.join(label for label, _ in sorted_detections)
        
        return digits


