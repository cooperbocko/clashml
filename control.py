import pyautogui
import time
import os
from PIL import Image
import matplotlib.pyplot as plt

class Control:
    
    #Provide top left and bottom right point to define the window
    def __init__(self, tx, ty, bx, by):
        self.tx = tx
        self.ty = ty
        self.bx = bx
        self.by = by
        
    def click(self, x, y):
        pyautogui.moveTo(self.tx + x, self.ty + y)
        pyautogui.click()
        
    def check_window_bounds(self):
        print("Move your mouse around. Press Ctrl+C to stop.")

        try:
            while True:
                x, y = pyautogui.position()
                print(f"Mouse position: ({x - self.tx}, {y - self.ty})", end='\r')  # Overwrites the line
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nDone.")
            
    def check_screen_bounds(self):
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
        region = (self.tx, self.ty, self.bx - self.tx, self.by - self.ty)
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
        
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
save_path = os.path.join(desktop, "screenshot.png")
screenshot = pyautogui.screenshot(region = (315, 890, 50, 50))
screenshot.save(save_path)
#c = Control(7, 70, 325, 760)
#c.check_screen_bounds()
#bluestacks coords: 0,25 - 549,978
#c.screenshot()

#screenshot = Image.open("screenshot_2025-10-13 21:26:03.139587.png")

#top left 633 240    668 272
#max_placement_img = c.get_cropped_images(screenshot, [(182, 272, 200, 295)])[0]
#elixr_img = c.get_cropped_images(screenshot, [(230, 623, 282, 678)])[0]
#plt.imshow(elixr_img)
#plt.show()
#0,25 for apple top bar

#iphone mirroring: 0, 70 - 325, 760