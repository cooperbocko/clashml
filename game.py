from merge import Merge
from control import Control
from card_matcher import CardMatch
from text_detect import TextDetect
import numpy as np
from ultralytics import YOLO
import cv2

class Game:
    #TODO: constans
    
    #screen bounds
    TOP = 68
    LEFT = 8
    BOTTOM = 966
    RIGHT = 423
    
    #card crop regions
    CARD_REGIONS = [
        (53, 782, 128, 874),
        (134, 782, 209, 874),
        (215, 782, 290, 874)
    ]
    
    #elixr crop region
    ELIXR_REGION = [(308, 822, 356, 872)]
    
    #placement region
    PLACEMENT_REGION = [(202, 355, 254, 386)]
    
    #click points
    
    def __init__(self):
        self.merge = Merge()
        self.control = Control(self.LEFT, self.TOP, self.RIGHT, self.BOTTOM) #TODO: make config file give screen size/constatns
        self.card_match = CardMatch() #TODO: make config file give screen size/constatns
        self.text_detection = TextDetect()
        self.digit_model = YOLO("models/clash_digits.pt")
        
    def play_game(self):
        #TODO: Get max place
        
        return
    
    def play_step(self):
        screenshot = self.control.screenshot()
        
        #TODO: Get elixir
        elixr_img = np.array(self.control.get_cropped_images(screenshot, self.ELIXR_REGION)[0])
        elixr_img = cv2.cvtColor(elixr_img, cv2.COLOR_RGBA2RGB)
        cv2.imwrite("text.png", elixr_img)
        elixr = self.digit_model.predict(source=elixr_img)
        results = elixr[0]
        boxes = results.boxes
        
        for box in boxes:
            cls_id = int(box.cls[0])       # class index (0-9)
            cls_name = results.names[cls_id]  # '0', '1', etc.
            conf = float(box.conf[0])      # confidence score
            x1, y1, x2, y2 = box.xyxy[0]  # bounding box coordinates

            print(f"Detected {cls_name} with {conf:.2f} at [{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}]")

        
        max_placement_img = np.array(self.control.get_cropped_images(screenshot, self.PLACEMENT_REGION)[0])
        pl = self.text_detection.detect_text(max_placement_img)
        print("max_placement: ", pl)

        #TODO: Get cards
        card_images = self.control.get_cropped_images(screenshot, self.CARD_REGIONS)
        
        cards = []
        for image in card_images:
            cards.append(self.card_match.match(image))
        print(cards)
        
        #TODO: Get agent move
    

game = Game()
game.play_step()