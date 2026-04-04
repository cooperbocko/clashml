from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageOps
import os
from dotenv import load_dotenv
import numpy as np
import cv2

class Roboflow:
    def __init__(self, model_id: str, env_path: str):
        load_dotenv(env_path)
        
        self.roboflow = InferenceHTTPClient(
            api_url='http://localhost:9001',
            api_key=os.getenv("ROBOFLOW_API_KEY")
        )
        self.model_id = model_id
        
        #dummy predict to load weights
        self.predict(Image.new('RGB', (5, 5)))
        
    def predict(self, image: Image):
        results = self.roboflow.infer(image, self.model_id)
        return results['predictions']
    
    def predict_all(self, images: list[Image]):
        return self.roboflow.infer(images, self.model_id)
        
    @staticmethod
    def preprocess_image(image: Image, auto_orient: bool, resize: bool, width: int, height: int, grayscale: bool, auto_adjust_contrast: bool):
        if auto_orient:
            image = ImageOps.exif_transpose(image)
        
        if resize:
            image = image.resize((width, height))
        
        if grayscale:
            image = image.convert('L')
        else:
            image = image.convert('RGB')
            
        image_array = np.array(image)
        if auto_adjust_contrast:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            
            if grayscale:
                image_array = clahe.apply(image_array)
            else:
                lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
                l, a, b = cv2.split(lab)
                l_updated = clahe.apply(l)
                image_array = cv2.merge((l_updated, a, b))
                image_array = cv2.cvtColor(image_array, cv2.COLOR_LAB2RGB)
        
        if grayscale and len(image_array.shape) == 2:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(image_array)
        