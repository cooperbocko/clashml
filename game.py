import pyautogui
from merge import Merge
from control import Control
from card_matcher import CardMatch
from text_detect import TextDetect
import numpy as np
from ultralytics import YOLO
import cv2
import random
import time

class Game:
    #TODO: constans
    NUM_HAND_SLOTS = 3
    NUM_BOARD_SLOTS = 25

    BUY_START = 0
    SELL_START = BUY_START + NUM_HAND_SLOTS
    MOVE_FRONT_START = SELL_START + NUM_BOARD_SLOTS
    MOVE_BACK_START = MOVE_FRONT_START + NUM_BOARD_SLOTS
    MOVE_BENCH_START = MOVE_BACK_START + NUM_BOARD_SLOTS
    NO_ACTION = MOVE_BENCH_START + NUM_BOARD_SLOTS
    TOTAL_ACTIONS = NO_ACTION + 1
    
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
    BATTLE = (220, 786)
    BOARD = [
        [(120, 600), (175, 600), (225, 600), (280, 600), (330, 600)],
        [(95, 640), (150, 565), (200, 565), (250, 565), (305, 565)],
        [(120, 680), (175, 680), (225, 680), (280, 680), (330, 680)],
        [(95, 720), (150, 720), (200, 720), (250, 720), (305, 720)],
        [(75, 785), (125, 785), (180, 785), (235, 785), (283, 785)]
    ]
    
    def __init__(self):
        self.merge = Merge()
        self.control = Control(self.LEFT, self.TOP, self.RIGHT, self.BOTTOM) #TODO: make config file give screen size/constatns
        self.card_match = CardMatch() #TODO: make config file give screen size/constatns
        self.text_detection = TextDetect()
        self.digit_model = YOLO("models/clash_digits_11.pt")
        
    def play_game(self):
        #TODO: click game button
        print('Starting game!')
        self.control.click(self.BATTLE[0], self.BATTLE[1])
        time.sleep(10)
        
        #TODO: get starting card
        #click 0,2
        print('Getting Starting Card!')
        start1 = self.BOARD[0][2]
        start2 = self.BOARD[3][2]
        self.control.click(start1[0], start1[1])
        time.sleep(1)
        #check if card screen appears
        color = pyautogui.pixel(416, 202)
        print(color)
        time.sleep(2)
        if color[0] not in range(58, 63) or color[1] not in range(54, 59) or color[2] not in range(79, 84):
            self.control.click(start2[0], start2[1])
            time.sleep(1)
            color = pyautogui.pixel(416, 202)
            print(color)
            time.sleep(2)
        start_screenshot = self.control.screenshot()
        #else click 3,2
        #screenshot
        #get crops
        start_card_image = self.control.get_cropped_images(start_screenshot, [(197, 143, 272, 237)])[0]
        start_card = self.card_match.match(start_card_image)
        self.merge.add_starting_card(str.upper(start_card), 1) #TODO: upper
        print('Added: ', start_card)
        self.control.click(400, 950)
        self.merge.print_map()
        
        #TODO: game loop
        print('Entering game loop!')
        game_over = False
        while not game_over:
            #deploy phase
            print('Starting Deploy phase!')
            while True: 
                self.play_step()
                end = pyautogui.pixel(109, 963)
                if end[0] == 22 and end[1] == 23 and end[2] == 41:
                    break
                self.merge.print_map()
                time.sleep(3)
                print('---------------------------------')
            
            #transition
            time.sleep(10)

            #battle phase
            print('Battle Phase')
            while True: #pixel check
                end = pyautogui.pixel(109, 963)
                if end[0] == 22 and end[1] == 23 and end[2] == 41:
                    break
                time.sleep(1)
                
            time.sleep(5)
                
            #TODO: detect game over
    
    def play_step(self):
        screenshot = self.control.screenshot()
        
        #TODO: Get elixir -> check back on results
        elixr_img = np.array(self.control.get_cropped_images(screenshot, self.ELIXR_REGION)[0])
        elixr_img = cv2.cvtColor(elixr_img, cv2.COLOR_RGBA2RGB)
        results = self.digit_model.predict(source=elixr_img)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        labels = [results.names[int(i)] for i in results.boxes.cls]
        sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
        digits = ''.join(label for label, _ in sorted_detections)
        elixr = int(digits)
        print("elixir: ", elixr)
        self.merge.elixir = elixr

        #TODO: easy ocr is not cutting it
        max_placement_img = np.array(self.control.get_cropped_images(screenshot, self.PLACEMENT_REGION)[0])
        max_placement = self.text_detection.detect_text(max_placement_img)
        if len(max_placement) > 0:
            max_placement = max_placement[0]
        print('Full Text: ', max_placement)
        if len(max_placement) > 0:
            max_placement = int(max_placement[len(max_placement) - 1]) #get last part of text
            print("max_placement: ", max_placement)
        self.merge.max_placement = 3 #TODO:

        #TODO: Get cards
        card_images = self.control.get_cropped_images(screenshot, self.CARD_REGIONS)
        cards = []
        for image in card_images:
            cards.append(str.upper(self.card_match.match(image))) #TODO: upper
        print(cards)
        self.merge.update_hand(cards[0], cards[1], cards[2])
        
        #TODO: Get state
        state = self.merge.get_state()
        #print(state)
        
        #TODO: Get agent move 0 - 105
        action, position = self.decode_action(random.randint(0, 4))
        print(f"action: {action}, position: {position}")
        row = int(position / 5)
        col = position % 5
        
        #TODO: Execute move
        if action == "buy":
            print("buying: ", position)
            self.merge.buy_card(position)
            if position == 0:
                self.control.click(100, 900)
            elif position == 1:
                self.control.click(175, 900)
            else:
                self.control.click(250, 900)
            return
        elif action == "sell":
            print("selling: ", row, col)
            self.merge.sell_card(row, col)
            spot = self.BOARD[row][col]
            self.control.drag(spot[0], spot[1], 100, 900)
            return
        elif action == "move_to_front":
            self.merge.move_to_front()
            return
        elif action == "move_to_back":
            self.merge.move_to_back()
            return
        elif action == "move_to_bench":
            self.merge.move_to_bench()
            return
        else:
            print("doing nothing")
            return
        
    def decode_action(self, action: int) -> tuple[str, int]:
        if action < self.SELL_START:
            return ("buy", action - self.BUY_START)
        elif action < self.MOVE_FRONT_START:
            return ("sell", action - self.SELL_START)
        elif action < self.MOVE_BACK_START:
            return ("move_to_front", action - self.MOVE_FRONT_START)
        elif action < self.MOVE_BENCH_START:
            return ("move_to_back", action - self.MOVE_BACK_START)
        elif action < self.NO_ACTION:
            return ("move_to_bench", action - self.MOVE_BENCH_START)
        else:
            return ("no_action", None)
        
        
g = Game()
g.play_game()

