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
        
    def click(self, point: Tuple[int, int]):
        pyautogui.moveTo(point[0], point[1])
        pyautogui.click()
        
    def drag(self, start_point: Tuple[int, int], end_point: Tuple[int, int]):
        pyautogui.moveTo(start_point[0], start_point[1])
        pyautogui.mouseDown()
        pyautogui.moveTo(end_point[0], end_point[1])
        pyautogui.mouseUp()
            
    def screenshot(self, filename: str="screenshot_pyautogui.png", path: str="~/Desktop/") -> Image:
        output_path = os.path.expanduser(f"{path}{filename}")
        region = (self.left, self.top, self.right - self.left, self.bottom - self.top)
        screenshot = pyautogui.screenshot(region = region)
        screenshot.save(output_path)
        return screenshot
    
    def get_cropped_images(self, screenshot: Image, regions: List[Tuple[int, int, int, int]]) -> list[Image]:
        cropped_images = []
        for region in regions:
            crop = screenshot.crop(region)

            # Always convert to RGB (flatten transparency correctly if RGBA)
            if crop.mode == "RGBA":
                background = Image.new("RGB", crop.size, (0, 0, 0))
                background.paste(crop, mask=crop.split()[3])  # apply alpha as mask
                crop = background
            else:
                crop = crop.convert("RGB")

            cropped_images.append(crop)
        return cropped_images
    
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
                color = pyautogui.pixel(x * 2, y * 2)
                print(f"Mouse position: ({x}, {y}) {color}", end='\r')  # Overwrites the line
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nDone.")

#Control.check_screen_bounds()
c = Control(0,0,0,0)
SAFE_CLICK = (400, 950)
BOARD = [
        [(120, 600), (175, 600), (225, 600), (280, 600), (330, 600)],
        [(95, 640), (150, 640), (200, 640), (250, 640), (305, 640)],
        [(120, 680), (175, 680), (225, 680), (280, 680), (330, 680)],
        [(95, 720), (150, 720), (200, 720), (250, 720), (305, 720)],
        [(75, 785), (125, 785), (180, 785), (235, 785), (283, 785)]
    ]
HAND = [
        (100, 900),
        (175, 900),
        (250, 900)
    ]
spot = BOARD[3][4]
c.click(point=SAFE_CLICK)
c.drag(spot, BOARD[4][4])