import cv2 
import numpy as np
import PIL

from control import Control

class DetectEdge: 
    def __init__(self, control: Control, points: list[list[list[int]]], buffer: int, threshold: int):
        self.control = control
        self.points = points
        self.buffer = buffer
        self.threshold = threshold
        
    def detect_edges(self, image: PIL.Image) -> list[list[int]]:
        rows = len(self.points)
        cols = len(self.points[0])
        
        res = [[0 for _ in range(rows)] for _ in range(cols)]
        for row in range(rows):
            for col in range(cols):
                point = self.points[row][col]
                point[0] += self.buffer
                point[1] += self.buffer
                region = point 
                crop = self.control.get_cropped_image(image, region)
                count, edge_map = self.check_edges(crop)
                if count >= self.threshold:
                    res[row][col] = count
        return res
        
    def check_edges(self, image: np.ndarray | PIL.Image):
        image = np.array(image)
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edge_count = np.sum(edges > 0)
        
        return edge_count, edges