import os

from PIL import Image
from polars import col

from control import Control
from config import Config

#To get screen bounds
#Control.check_screen_bounds(True)
#Windows users can use the code below to easily get the window bounds
'''
from pywinauto import Application
app = Application().connect(title="BlueStacks App Player 1")
window = app.window(title="BlueStacks App Player 1")
rect = window.rectangle()
print(f"Rectangle: {rect}")
print(f"Left: {rect.left}, Top: {rect.top}, Right: {rect.right}, Bottom: {rect.bottom}")
'''

#Create Control Object with screen bounds
c = Control(0, 65, 517, 985, 0)

#Get screenshots for config file
def on_press():
    os.makedirs("images/game_screenshots", exist_ok=True)

    i = 0
    while True:
        key = input("Press a key to take a screen shot: ")
        filename = f"screenshot{i}.png"
        path = 'images/game_screenshots'
        s = c.screenshot()
        s.save(os.path.join(path, filename))
        i += 1
#on_press()

#Get crops from screenshots of the phase icons
phase_region = [[250, 388, 289, 438]]
def make_phase_picture():
    path = 'images/game_screenshots'
    filename = 'screenshot0_phase.png'
    s = Image.open('images\game_screenshots\screenshot0.png')
    phase = c.get_cropped_images(s, phase_region)[0]
    phase.save(os.path.join(path, filename))
#make_phase_picture()

#Used to check the regions from you config file
def test_regions():
    config = Config.load_from_json("./configs/mac.json")
    c = Control(config.screen_bounds.left, config.screen_bounds.top, config.screen_bounds.right, config.screen_bounds.bottom, 0)
    key = input("Press a key to take a screen shot: ")
    filename = f"screenshot.png"
    path = 'images/game_screenshots'
    s = c.screenshot()
    s.save(os.path.join(path, filename))
    
    i = 1
    for region in config.regions.card_regions:
        card = c.get_cropped_image(s, region)
        card.save(f"{path}/card_{i}.png")
        i += 1
        
    phase = c.get_cropped_image(s, config.regions.phase_region)
    phase.save(f"{path}/phase.png")
    
    level = c.get_cropped_image(s, config.regions.card_level_region)
    level.save(f"{path}/level.png")
    
    card_pic = c.get_cropped_image(s, config.regions.card_picture_region)
    card_pic.save(f"{path}/card_pic.png")
    
    elixir = c.get_cropped_image(s, config.regions.elixr_region)
    elixir.save(f"{path}/elixir.png")
    
    defeated = c.get_cropped_image(s, config.regions.defeated_region)
    defeated.save(f"{path}/defeated.png")
    
    ok = c.get_cropped_image(s, config.regions.ok_region)
    ok.save(f"{path}/ok.png")
    
    again = c.get_cropped_image(s, config.regions.play_again_region)
    again.save(f"{path}/again.png")    
#test_regions()

def test_colors():
    config = Config.load_from_json("./configs/mac.json")
    c = Control(config.screen_bounds.left, config.screen_bounds.top, config.screen_bounds.right, config.screen_bounds.bottom, 0)
    key = input("Press a key to take a screen shot: ")
    filename = f"screenshot.png"
    path = 'images/game_screenshots'
    s = c.screenshot()
    s.save(os.path.join(path, filename))
    
    x = config.click_points.end_bar[0]
    y = config.click_points.end_bar[1]
    region = [x - 1, y - 1, x + 1, y + 1]
    color = c.get_cropped_image(s, region)
    color.save(f"{path}/color.png")
test_colors()
    
    
    
    

