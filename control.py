import pyautogui
import time
import os

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
            
    def screenshot(self, filename="screenshot_pyautogui.png"):
        
        output_path = os.path.expanduser(f"~/Desktop/{filename}")
        region = (self.tx, self.ty, self.bx, self.by - self.ty)
        screenshot = pyautogui.screenshot(region = region)
        screenshot.save(output_path)
        print(f"Screenshot saved to {output_path}")


c = Control(0, 25, 549, 978)

#bluestacks coords: 0,25 - 549,978
c.screenshot()
c.click(265, 745)
c.click(265, 745)

#0,25 for apple top bar