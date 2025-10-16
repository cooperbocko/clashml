from merge import Merge
from control import Control
from card_matcher import CardMatch
from text_detect import TextDetect
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

class Game:
    #TODO: constans
    SCREENSHOT_PATH = "~/Desktop/"
    SCREENSHOT_NAME = "screenshot_pyautogui.png"
    
    def __init__(self):
        self.merge = Merge()
        self.control = Control(0, 0, 0, 0) #TODO: make config file give screen size/constatns
        self.card_match = CardMatch() #TODO: make config file give screen size/constatns
        self.text_detection = TextDetect()
        
    def play_game(self):
        #TODO: Get max place
        max_placement_img = np.array(self.control.get_cropped_images(screenshot, [(182, 272, 200, 295)])[0])
        pl = self.text_detection.detect_text(max_placement_img)
        print(pl)
        return
    
    def play_step(self):
        #screenshot = self.control.screenshot()
        screenshot = Image.open("images/game_screenshots/screenshot_2025-10-12 20:56:52.404359.png")
        #TODO: Get elixir
        elixr_img = np.array(self.control.get_cropped_images(screenshot, [(220, 613, 292, 688)])[0])
        plt.imshow(elixr_img)
        plt.show()
        elixr = self.text_detection.detect_text(elixr_img)
        print(elixr)
        return

        #TODO: Get cards
        card_regions = [
            (43, 600,  99, 670),
            (105, 600, 161, 670),
            (167, 600, 223, 670)
        ]
        card_images = self.control.get_cropped_images(screenshot, card_regions)
        
        cards = []
        for image in card_images:
            cards.append(self.card_match.match(image))
        print(cards)
    

game = Game()
game.play_step()