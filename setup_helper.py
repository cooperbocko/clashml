import os

from PIL import Image

from control import Control

#To get screen bounds
#Control.check_screen_bounds()

#Create Control Object with screen bounds
c = Control(0, 34, 605, 1114, 0)

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

