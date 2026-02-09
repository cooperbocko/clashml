from PIL import Image
import pyautogui
import time

class Control:
    
    def __init__(self, left: int, top: int, right: int, bottom: int, click_delay):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.click_delay = click_delay
        
    def click(self, point: list[int]):
        pyautogui.moveTo(point[0] + self.left, point[1] + self.top)
        pyautogui.click()
        time.sleep(self.click_delay)
        
    def drag(self, start_point: list[int], end_point: list[int]):
        pyautogui.moveTo(start_point[0] + self.left, start_point[1] + self.top)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_point[0] + self.left, end_point[1] + self.top)
        pyautogui.mouseUp()
        time.sleep(self.click_delay)
            
    def screenshot(self) -> Image:
        region = (self.left, self.top, self.right - self.left, self.bottom - self.top)
        screenshot = pyautogui.screenshot(region = region)
        return screenshot
    
    def check_pixel(self, point: list[int], is_mac_laptop_screen:bool = False) -> tuple[int, int, int]:
        x, y = point
        x = x + self.left
        y = y + self.top
        if is_mac_laptop_screen:
            x = x * 2
            y = y * 2
        
        return pyautogui.pixel(x, y)
    
    def get_cropped_image(self, screenshot: Image, region: list[int]) -> Image:
        crop = screenshot.crop(region)

        # Always convert to RGB (flatten transparency correctly if RGBA)
        if crop.mode == "RGBA":
            background = Image.new("RGB", crop.size, (0, 0, 0))
            background.paste(crop, mask=crop.split()[3])  # apply alpha as mask
            crop = background
        else:
            crop = crop.convert("RGB")

        return crop
    
    #For checking coordinates inside of game screen
    def check_window_bounds(self):
        print("Move your mouse around. Press Ctrl+C to stop.")

        try:
            while True:
                x, y = pyautogui.position()
                print(f"Mouse position: ({x - self.left}, {y - self.top})", end='\r') 
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nDone.")
            
    #For checking coordiantes on your actual screen        
    @staticmethod
    def check_screen_bounds(is_mac_laptop_screen):
        print("Move your mouse around. Press Ctrl+C to stop.")

        try:
            while True:
                x, y = pyautogui.position()
                if is_mac_laptop_screen:
                    color = pyautogui.pixel(x * 2, y * 2)
                else:
                    color = pyautogui.pixel(x, y)
                print(f"Mouse position: ({x}, {y}) {color}", end='\r') 
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nDone.")