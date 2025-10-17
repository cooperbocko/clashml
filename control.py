import pyautogui
import time
import os

class Control:
    
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        
    def click(self, x, y):
        pyautogui.moveTo(self.left + x, self.top + y)
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
                print(f"Mouse position: ({x}, {y})", end='\r')  # Overwrites the line
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nDone.")
            
    def screenshot(self, filename="screenshot_pyautogui.png", path="~/Desktop/"):
        output_path = os.path.expanduser(f"{path}{filename}")
        region = (self.left, self.top, self.right - self.left, self.bottom - self.top)
        screenshot = pyautogui.screenshot(region = region)
        screenshot.save(output_path)
        print(f"Screenshot saved to {output_path}")
        return screenshot
    
    def get_cropped_images(self, screenshot, regions):
        cropped_images = []
        for region in regions:
            crop = screenshot.crop(region)
            cropped_images.append(crop)
        return cropped_images
