from control import Control
from datetime import datetime
import time
from PIL import Image
import os
from config import Config

config_path = "./configs/mac.json"
config = Config.load_from_json(config_path)

c = Control(config.screen_bounds.left, config.screen_bounds.top, config.screen_bounds.right, config.screen_bounds.bottom, 0)

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
        s = c.screenshot()
        s.save("./images/game_screenshots/screen.png")
        path = 'images/game_screenshots'
        
        for region in config.regions.card_regions:
            print(region)
            filename = f"screenshot_{datetime.now()}.png"
            card = c.get_cropped_image(s, region)
            card.save(f"{path}/{filename}")
        
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
                
                
on_press()