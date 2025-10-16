from control import Control
from datetime import datetime
import time

c = Control(7, 70, 325, 760)
elixr = Control(315, 890, 365, 940)

def constant():
    while True:
        filename1 = f"screenshot_{datetime.now()}.png"
        filename2 = f"screenshot_{datetime.now()}.png"
        #c.screenshot(filename=filename1, path='images/game_screenshots/')
        elixr.screenshot(filename=filename2, path='images/game_screenshots/')
        time.sleep(5)
        
def on_press():
    while True:
        key = input("Press a key: ")
        print(f"You pressed: {key}")
        filename = f"screenshot_{datetime.now()}.png"
        c.screenshot(filename=filename, path='images/game_screenshots/')
        

constant()