from control import Control
from datetime import datetime
import time

CARD_PICTURE_REGION = [(197, 143, 272, 237)]
c = Control(8, 68, 423, 966)
elixr = Control(315, 890, 365, 940)
timez = Control(350, 220, 390, 270)
place = Control(175, 400, 275, 475)
card_picture = Control(197 + 8, 143 + 68, 272 + 8, 237 + 68)
card_level = Control(291, 225, 310, 243)

def constant():
    count = 0
    while True:
        count += 1
        print(count * 3)
        filename1 = f"screenshot_{datetime.now()}.png"
        #filename2 = f"screenshot_{datetime.now()}.png"
        #filename3 = f"screenshot_{datetime.now()}.png"
        #elixr.screenshot(filename=filename1, path='images/game_screenshots/')
        #timez.screenshot(filename=filename2, path='images/game_screenshots/')
        #place.screenshot(filename=filename3, path='images/game_screenshots/')
        c.screenshot(filename=filename1, path='images/game_screenshots/')
        time.sleep(5)
        
def on_press():
    while True:
        key = input("Press a key: ")
        print(f"You pressed: {key}")
        filename = f"screenshot_{datetime.now()}.png"
        c.screenshot(filename=filename, path='images/game_screenshots/')
        
filename1 = f"screenshot_{datetime.now()}.png"
c.screenshot()