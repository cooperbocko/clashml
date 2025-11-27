from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient
from PIL import Image
import os
from dotenv import load_dotenv


class DetectDigits:
    def __init__(self, is_roboflow, model_path, env_path):
        load_dotenv(env_path)
        
        self.is_roboflow = is_roboflow
        self.yolo = YOLO(model_path)
        self.roboflow = InferenceHTTPClient(
            api_url='https://detect.roboflow.com',
            api_key=os.getenv("ROBOFLOW_API_KEY")
        )
        
    def predict(self, image):
        digits = ''
        if self.is_roboflow:
            results = self.roboflow.infer(image, model_id='clash-digit-detection-zjhdw/2')['predictions']
            sorted_predictions = sorted(results, key=lambda r: r['x'])
            for prediction in sorted_predictions:
                print(prediction['class'])
                digits = digits + prediction['class']
        else:
            results = self.yolo.predict(source=image, verbose=False)[0]
            boxes = results.boxes.xyxy.cpu().numpy()
            labels = [results.names[int(i)] for i in results.boxes.cls]
            sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
            digits = ''.join(label for label, _ in sorted_detections)
        
        return int(digits)


