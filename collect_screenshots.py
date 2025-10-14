from control import Control
from datetime import datetime
import time

c = Control(7, 70, 325, 760)

def constant():
    while True:
        filename = f"screenshot_{datetime.now()}.png"
        c.screenshot(filename=filename, path='images/game_screenshots/')
        time.sleep(5)
        
def on_press():
    while True:
        key = input("Press a key: ")
        print(f"You pressed: {key}")
        filename = f"screenshot_{datetime.now()}.png"
        c.screenshot(filename=filename, path='images/game_screenshots/')
        
on_press()
