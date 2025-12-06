from control import Control
from datetime import datetime
import time
from PIL import Image
import os

CARD_PICTURE_REGION = [(197, 143, 272, 237)]
card_regions = [[81, 786, 153, 876], [162, 786, 234, 876], [243, 786, 313, 876]]
phase_region = [[164, 352, 196, 393]]

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
        path = 'images/game_screenshots'
        s = c.screenshot()
        s.save(os.path.join(path, filename))
        
def get_pics():
    path = './images/game_screenshots'
    
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            image = Image.open(file_path)
            images = c.get_cropped_images(image, phase_region)
            
            x = 0
            for image in images:
                time = datetime.now()
                image.save(f'./images/raw_cards/{x}{time}.png')
                x += 1
                
                
get_pics()