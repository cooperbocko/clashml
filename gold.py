from ultralytics import YOLO
from PIL import Image

from roboflow import Roboflow

class DetectGold:
    def __init__(self, is_roboflow: bool, model_path: str, env_path: str):
        self.is_roboflow = is_roboflow
        self.yolo = YOLO(model_path)
        self.roboflow = Roboflow('merge-gold-circle-detect-8yzjn/3', env_path)
        
    def predict(self, image: Image):
        image = Roboflow.preprocess_image(image)
        
        if self.is_roboflow:
            return self.roboflow.predict(image)
        else:
            return self.yolo.predict(source=image, verbose=False)[0]