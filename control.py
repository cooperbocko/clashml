from ast import Tuple
from PIL import Image
import pyautogui
import time
import os
from typing import List, Tuple

class Control:
    
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        
    def click(self, x: int, y: int):
        pyautogui.moveTo(x, y)
        pyautogui.click()
        
    def check_window_bounds(self):
        print("Move your mouse around. Press Ctrl+C to stop.")

        try:
            while True:
                x, y = pyautogui.position()
                print(f"Mouse position: ({x - self.left}, {y - self.top})", end='\r')  # Overwrites the line
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nDone.")
            
    @staticmethod
    def check_screen_bounds():
        print("Move your mouse around. Press Ctrl+C to stop.")

        try:
            while True:
                x, y = pyautogui.position()
                color = pyautogui.pixel(x, y)
                print(f"Mouse position: ({x}, {y}) {color}", end='\r')  # Overwrites the line
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nDone.")
            
    def screenshot(self, filename: str="screenshot_pyautogui.png", path: str="~/Desktop/") -> Image:
        output_path = os.path.expanduser(f"{path}{filename}")
        region = (self.left, self.top, self.right - self.left, self.bottom - self.top)
        screenshot = pyautogui.screenshot(region = region)
        screenshot.save(output_path)
        print(f"Screenshot saved to {output_path}")
        return screenshot
    
    def get_cropped_images(self, screenshot: Image, regions: List[Tuple[int, int, int, int]]) -> list[Image]:
        cropped_images = []
        for region in regions:
            crop = screenshot.crop(region)
            cropped_images.append(crop)
        return cropped_images

#Control.check_screen_bounds()