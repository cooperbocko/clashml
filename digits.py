from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageOps
import os
from dotenv import load_dotenv
import numpy as np
import cv2


class DetectDigits:
    def __init__(self, is_roboflow, model_path, env_path):
        load_dotenv(env_path)
        
        self.is_roboflow = is_roboflow
        self.yolo = YOLO(model_path)
        self.roboflow = InferenceHTTPClient(
            api_url='https://detect.roboflow.com',
            api_key=os.getenv("ROBOFLOW_API_KEY")
        )
        
    def preprocess_image(self, image):
        # 1. Auto-Orient: Applied (using Pillow's ImageOps)
        # This reads the EXIF data and rotates the image if necessary.
        image = ImageOps.exif_transpose(image)
        
        # 2. Resize: Stretch to 640x640 (using Pillow's resize)
        image = image.resize((640, 640))
        
        # 3. Grayscale: Applied
        # Convert Pillow image to Grayscale (L mode)
        image = image.convert('L') 
        
        # Convert Pillow image to OpenCV format (NumPy array) for CLAHE
        img_array = np.array(image)
        
        # 4. Auto-Adjust Contrast: Using Adaptive Equalization (CLAHE)
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        # CLAHE must be applied to a single-channel (grayscale) image
        processed_array = clahe.apply(img_array)
        
        # Convert the NumPy array back to a Pillow Image object
        processed_image = Image.fromarray(processed_array)
        
        return processed_image
        
    def predict(self, image):
        image = self.preprocess_image(image)
        digits = ''
        if self.is_roboflow:
            results = self.roboflow.infer(image, model_id='clash-digit-detection-zjhdw/5')['predictions']
            print(results)
            sorted_predictions = sorted(results, key=lambda r: r['x'])
            print(sorted_predictions)
            for prediction in sorted_predictions:
                digits = digits + prediction['class']
        else:
            results = self.yolo.predict(source=image, verbose=False)[0]
            boxes = results.boxes.xyxy.cpu().numpy()
            labels = [results.names[int(i)] for i in results.boxes.cls]
            sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
            digits = ''.join(label for label, _ in sorted_detections)
        
        return digits


