import easyocr
import cv2
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore", message=".*pin_memory.*")

class TextDetect:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], model_storage_directory='models', gpu=True)
        
    def detect_text(self, image: Image) -> list:
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        return self.reader.readtext(image, detail=0)