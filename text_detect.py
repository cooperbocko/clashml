import easyocr
import cv2
from PIL import Image
import warnings
warnings.filterwarnings("ignore", message=".*pin_memory.*")

class TextDetect:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], model_storage_directory='models')
        
    def detect_text(self, image: Image) -> list:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        return self.reader.readtext(image, detail=0)