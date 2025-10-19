import easyocr
import cv2
from PIL import Image

class TextDetect:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], model_storage_directory='models')
        
    def detect_text(self, image: Image):
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        return self.reader.readtext(image, detail=0)