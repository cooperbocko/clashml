from unittest import result
from ultralytics import YOLO
from PIL import Image

from roboflow import Roboflow

class DetectGold:
    def __init__(self, is_roboflow: bool, model_path: str, env_path: str):
        self.is_roboflow = is_roboflow
        self.yolo = YOLO(model_path)
        self.roboflow = Roboflow('merge-gold-circle-detect-8yzjn/3', env_path)
        
    def predict(self, image: Image) -> tuple[bool, list[list]]:
        width, height = image.size
        image = Roboflow.preprocess_image(image)
        pwidth, pheight = image.size
        
        wratio = width / pwidth
        hratio = height / pheight
        
        points = []
        
        if self.is_roboflow:
            results =  self.roboflow.predict(image)
            if result == None:
                return (False, points)
            if len(results) > 0:
                for prediction in results:
                    x = prediction['x']
                    y = prediction['y']
                    width = prediction['width']
                    height = prediction['height']
                    
                    x = int((x + width/2) * wratio)
                    y = int((y + height/2) * hratio)
                    points.append([x,y])
                return (True, points)
            return (False, points)
        else:
            results = self.yolo.predict(source=image, verbose=False)[0]
            boxes = results.boxes.xyxy.cpu().numpy()
            if len(boxes) > 0:
                for box in boxes:
                    x1, y1, x2, y2 = box.astype(int)
                    x = int(((x1 + x2)/2) * wratio)
                    y = int(((y1 + y2)/2) * hratio)
                    points.append([x,y])
                return (True, points)
            return (False, points)