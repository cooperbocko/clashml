import pyautogui
from sympy import false
from merge import Merge
from control import Control
from card_matcher import CardMatch
from text_detect import TextDetect
from PIL import Image
import numpy as np
from ultralytics import YOLO
import cv2
import random
import time
import matplotlib.pyplot as plt

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
    CARD_PICTURE_REGION = [(197, 143, 272, 237)]
    
    #click points
    BATTLE = (220, 786)
    BOARD = [
        [(120, 600), (175, 600), (225, 600), (280, 600), (330, 600)],
        [(95, 640), (150, 640), (200, 640), (250, 640), (305, 640)],
        [(120, 680), (175, 680), (225, 680), (280, 680), (330, 680)],
        [(95, 720), (150, 720), (200, 720), (250, 720), (305, 720)],
        [(75, 785), (125, 785), (180, 785), (235, 785), (283, 785)]
    ]
    HAND = [
        (100, 900),
        (175, 900),
        (250, 900)
    ]
    CARD_PRESENT = (416, 202)
    CARD_PRESENT_COLORS = [31, 31, 53] #60, 56, 81
    SAFE_CLICK = (400, 950)
    END_BAR = (109, 963) #~5 seconds
    END_COLOR = [23, 25, 46]
    
    def __init__(self):
        self.merge = Merge()
        self.control = Control(self.LEFT, self.TOP, self.RIGHT, self.BOTTOM) #TODO: make config file give screen size/constatns
        self.card_match = CardMatch() #TODO: make config file give screen size/constatns
        self.text_detection = TextDetect()
        self.digit_model = YOLO("models/clash_digits_11.pt")
        
    def play_game(self):
        #TODO: click game button
        print('Starting game!\n')
        self.control.click(self.BATTLE)
        time.sleep(10)
        
        #TODO: get starting card
        print('Getting Starting Card!')
        start1 = self.BOARD[0][2]
        start2 = self.BOARD[3][2]
        self.control.click(start1)
        start_card_image = pyautogui.screenshot(region=(self.CARD_PICTURE_REGION[0][0] + self.LEFT, self.CARD_PICTURE_REGION[0][1] + self.TOP, (self.CARD_PICTURE_REGION[0][2] - self.CARD_PICTURE_REGION[0][0]), (self.CARD_PICTURE_REGION[0][3] - self.CARD_PICTURE_REGION[0][1])))
        start_card = self.card_match.match(start_card_image)
        if (start_card == 'no_card'):
            self.control.click(start2)
            start_card_image = pyautogui.screenshot(region=(self.CARD_PICTURE_REGION[0][0] + self.LEFT, self.CARD_PICTURE_REGION[0][1] + self.TOP, (self.CARD_PICTURE_REGION[0][2] - self.CARD_PICTURE_REGION[0][0]), (self.CARD_PICTURE_REGION[0][3] - self.CARD_PICTURE_REGION[0][1])))
            start_card = self.card_match.match(start_card_image)
        self.merge.add_starting_card(str.upper(start_card), 1)
        print('Added: ', start_card)
        print('')
        self.control.click(self.SAFE_CLICK)
        self.merge.print_map()
        
        #TODO: game loop
        print('Entering game loop!\n')
        game_over = False
        game_round = 0
        while not game_over:
            game_round += 1
            print(f'----------Round {game_round}-----------------------\n')
            #deploy phase
            print('Starting Deploy phase!')
            move = 0
            while True: 
                move += 1
                print(f'----------Move {move}-----------------------\n')
                self.play_step(game_round, move)
                #TODO: only for mac laptop display do you have to multiply by 2
                end = pyautogui.pixel(self.END_BAR[0] * 2, self.END_BAR[1] * 2)
                if end[0] <= self.END_COLOR[0] + 20 and end[1] <= self.END_COLOR[1] + 20 and end[2] <= self.END_COLOR[2] + 20:
                    break
                
                print('current map:')
                self.merge.print_map()
                time.sleep(3)
            
            #transition
            time.sleep(10)

            #battle phase
            print('Battle Phase')
            while True: #pixel check
                end = pyautogui.pixel(self.END_BAR[0] * 2, self.END_BAR[1] * 2)
                print('end: ', end)
                if end[0] <= self.END_COLOR[0] + 20 and end[1] <= self.END_COLOR[1] + 20 and end[2] <= self.END_COLOR[2] + 20:
                    break
                time.sleep(1)
                
            time.sleep(5)
                
            #TODO: detect game over
    
    def play_step(self, n_round, n_move):
        screenshot = self.control.screenshot(filename=f"{n_round}{n_move}screenshot.png", path="logs/")
        
        #TODO: Get elixir -> check back on results and do error checking
        elixr_img = self.control.get_cropped_images(screenshot, self.ELIXR_REGION)[0]
        elixr_img.save(f"logs/{n_round}{n_move}elixr.png")
        elixr_img = np.array(elixr_img, dtype=np.uint8)
        results = self.digit_model.predict(source=elixr_img, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        labels = [results.names[int(i)] for i in results.boxes.cls]
        sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
        digits = ''.join(label for label, _ in sorted_detections)
        elixr = int(digits)
        print("elixir: ", elixr)
        self.merge.elixir = elixr

        #TODO: easy ocr is not cutting it or is it
        max_placement_img = self.control.get_cropped_images(screenshot, self.PLACEMENT_REGION)[0]
        max_placement_img.save(f"logs/{n_round}{n_move}max_placement.png")
        max_placement_img = np.array(self.control.get_cropped_images(screenshot, self.PLACEMENT_REGION)[0])
        max_placement = self.text_detection.detect_text(max_placement_img)
        if len(max_placement) > 0:
            max_placement = max_placement[0]
        print('Full Text: ', max_placement)
        if len(max_placement) > 0:
            max_placement = int(max_placement[len(max_placement) - 1]) #get last part of text
            print("max_placement: ", max_placement)
        self.merge.max_placement = max_placement #TODO: change this

        #TODO: Get cards
        card_images = self.control.get_cropped_images(screenshot, self.CARD_REGIONS)
        cards = []
        for image in card_images:
            cards.append(str.upper(self.card_match.match(image))) #TODO: upper
        print("Hand: ", cards)
        self.merge.update_hand(cards[0], cards[1], cards[2])
        
        #TODO: Get state
        state = self.merge.get_state()
        #print(state)
        
        #TODO: Get agent move 0 - 105
        action, position = self.decode_action(random.randint(0, 104))
        print(f"action: {action}, position: {position}")
        row = int(position / 5)
        col = position % 5
        fpoint = self.BOARD[row][col]
        
        #TODO: Execute move
        if action == "buy":
            print("buying: ", position)
            self.merge.buy_card(position)
            if position == 0:
                self.control.click(self.HAND[0])
            elif position == 1:
                self.control.click(self.HAND[1])
            else:
                self.control.click(self.HAND[2])
            return
        elif action == "sell":
            print("selling: ", row, col)
            self.merge.sell_card(row, col)
            self.control.drag(fpoint, self.HAND[0])
            return
        elif action == "move_to_front":
            print(f"Moving: {row}{col} to the front!")
            _, r, c = self.merge.move_to_front(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
            return
        elif action == "move_to_back":
            print(f"Moving: {row}{col} to the back!")
            _, r, c = self.merge.move_to_back(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
            return
        elif action == "move_to_bench":
            print(f"Moving: {row}{col} to the bench!")
            _, r, c = self.merge.move_to_bench(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
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

