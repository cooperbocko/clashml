import os

import cv2
import numpy as np
from PIL import Image

class TemplateMatch:
    def __init__(self, threshhold: float, folder_path: str):
        self.threshold = threshhold
        self.folder_path = folder_path
        self.templates = []
        self.load_templates()
        
    def load_templates(self):
        for filename in os.listdir(self.folder_path):
            path = os.path.join(self.folder_path, filename)
            template = cv2.imread(path)
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            self.templates.append(template)
        
    def detect(self, screenshot: Image) -> bool:
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        for template in self.templates:
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            minv, maxv, minl, maxl = cv2.minMaxLoc(result)
            if maxv >= self.threshold:
                return True
            
        return False
    
    