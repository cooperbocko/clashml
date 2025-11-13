import pyautogui
from merge import Merge
from control import Control
from card_matcher import CardMatch
from text_detect import TextDetect
from image_match import ImageMatch
from dqn import DQN, QTrainer, ReplayBuffer
from PIL import Image
import numpy as np
from ultralytics import YOLO
import torch
import cv2
import random
import time
import matplotlib.pyplot as plt
import os

class Game:
    #system settings
    IS_MAC_LAPTOP_SCREEN = True
    
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
    
    EPSILON = 0
    EPSILON_MIN = 0.05
    EPSILON_DECAY = 0.995
    
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
    PLACEMENT_REGION = [(199, 352, 257, 389)] #crop
    CARD_PICTURE_REGION = [(197, 143, 272, 237)] #crop
    CARD_LEVEL_REGION = [(291, 225, 310, 243)] #screen shot
    
    DEFEATED_REGION = [(155, 179, 259, 202)]
    PLAY_AGAIN_REGION = [(43, 786, 201, 840)]
    OK_REGION = [(214, 786, 372, 840)]
    
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
    PLAY_AGAIN = (122, 879)
    OK = (300, 880)
    
    def __init__(self):
        self.merge = Merge()
        self.control = Control(self.LEFT, self.TOP, self.RIGHT, self.BOTTOM) #TODO: make config file give screen size/constatns
        self.card_match = CardMatch() #TODO: make config file give screen size/constatns
        self.level_match = ImageMatch("level_match_db.npz", "images/levels")
        self.text_detection = TextDetect()
        self.digit_model = YOLO("models/clash_digits_11.pt")
        self.gold_detection = YOLO("models/gold_circle_11.pt")
        self.policy_net = DQN(len(self.merge.get_state()), 128, self.TOTAL_ACTIONS)
        self.target_net = DQN(len(self.merge.get_state()), 128, self.TOTAL_ACTIONS)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.replay_buffer = ReplayBuffer()
        self.trainer = QTrainer(self.policy_net, self.target_net, self.replay_buffer, 1e-3, 0.99)
        self.e = self.EPSILON
        
    def train(self, n_games):
        best = 0
        
        self.control.click(self.BATTLE)
        
        for i in range(n_games - 1):
            if not os.path.isdir(f'logs/{i}'):
                os.mkdir(f'logs/{i}')
            time.sleep(10)
            
            run = self.play_game(i)
            if run > best:
                best = run
                self.policy_net.save('./models', 'best_merge.pth')
            self.target_net.load_state_dict(self.policy_net.state_dict())

            self.merge = Merge()
            self.control.click(self.PLAY_AGAIN)
        self.play_game(n_games - 1)
        
    def play_game(self, n_game):
        total_reward = 0
        print('Starting game!\n')
        
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
        
        print('Entering game loop!\n')
        game_over = False
        game_round = 0
        state = self.update_state(n_game, game_round, 0)
        while not game_over:
            states = []
            actions = []
            rewards = []
            next_states = []
            dones = []
            
            game_round += 1
            print(f'----------Round {game_round}-----------------------\n')
            print('Starting Deploy phase!')
            move = 0
            while True: 
                move += 1
                print(f'----------Move {move}-----------------------\n')
                #self.play_step(game_round, move)
                
                self.gold_check()
                #state = self.update_state(n_game, game_round, move)
                #print('state: ', state)
                states.append(state)
                #TODO: Get agent move 0 - 105
                if random.random() < self.e:
                    print('random action')
                    action = random.randint(0, self.TOTAL_ACTIONS - 1)
                else:
                    with torch.no_grad():
                        print('dqn action')
                        q_values = self.policy_net(torch.FloatTensor(state))
                        action = q_values.argmax().item()
                self.e = max(self.EPSILON_MIN, self.e * self.EPSILON_DECAY)
                actions.append(action)
                reward = self.do_action(action)
                total_reward += reward
                print('reward: ', reward)
                rewards.append(reward)
                state = self.update_state(n_game, game_round, move + 1)
                next_states.append(state)
                #next_states.append(self.update_state(n_game, game_round, move + 1))
                dones.append(False)
                
                end = self.control.check_pixel(self.END_BAR, self.IS_MAC_LAPTOP_SCREEN)
                print("end: ", end)
                if end[0] <= self.END_COLOR[0] + 20 and end[1] <= self.END_COLOR[1] + 20 and end[2] <= self.END_COLOR[2] + 20:
                    break
                
                print('current map:')
                self.merge.print_map()
                #time.sleep(1)
            
            #transition
            time.sleep(10)

            print('Battle Phase')
            while True: 
                end = self.control.check_pixel(self.END_BAR, self.IS_MAC_LAPTOP_SCREEN)
                print('end: ', end)
                if end[0] <= self.END_COLOR[0] + 20 and end[1] <= self.END_COLOR[1] + 20 and end[2] <= self.END_COLOR[2] + 20:
                    break
                
                #TODO: detect game over
                screenshot = self.control.screenshot()
                ok_image = np.array(self.control.get_cropped_images(screenshot, self.OK_REGION)[0])
                play_again_image = np.array(self.control.get_cropped_images(screenshot, self.PLAY_AGAIN_REGION)[0])
                ok = self.text_detection.detect_text(ok_image)
                play_again = self.text_detection.detect_text(play_again_image)
                
                if len(ok) > 0:
                    print("ok: ", ok)
                
                if len(play_again) > 0:
                    print("play again: ", play_again)
                    game_over = True
                    dones[len(dones) - 1] = True
                    time.sleep(3)
                    screenshot = self.control.screenshot()
                    defeated_image = np.array(self.control.get_cropped_images(screenshot, self.DEFEATED_REGION)[0])
                    defeated = self.text_detection.detect_text(defeated_image)
                    if len(defeated) > 0:
                        defeated = str.lower(defeated[0])
                    print(defeated)
                    if defeated == 'defeated':
                        rewards[len(rewards) - 1] += 30
                        total_reward += 30
                    else:
                        rewards[len(rewards) - 1] -= 30
                        total_reward -= 30
                    break
                
                #train
                self.trainer.train_step(32)
                time.sleep(1)
                
            self.replay_buffer.push(states, actions, rewards, next_states, dones)
            time.sleep(5)
        
        print('Game Over!')
        print('Total Reward: ', total_reward)
        return total_reward
    
    def play_step(self, n_round, n_move):
        screenshot = self.control.screenshot(filename=f"{n_round}{n_move}screenshot.png", path="logs/")
        
        #Check for golden circles
        gold_results = self.gold_detection.predict(source=screenshot, verbose=False)[0]
        if len(gold_results.boxes) > 0:
            print('Detected gold circle(s)!')
            for box in gold_results.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = box.astype(int)
                x = int((x1 + x2)/2)
                y = int((y1 + y2)/2)
                point = (self.LEFT + x, self.TOP + y)
                print(f'Clicking: x:{x} y:{y}')
                self.control.click(point)
                time.sleep(3)
                self.recheck_board()
        
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
        max_placement_img = np.array(max_placement_img, dtype=np.uint8)
        results = self.digit_model.predict(source=max_placement_img, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        labels = [results.names[int(i)] for i in results.boxes.cls]
        sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
        digits = ''.join(label for label, _ in sorted_detections)
        if len(digits) > 0:
            max_placement = int(digits[len(digits) - 1])
            print("max_placement: ", max_placement)
            self.merge.max_placement = max_placement

        #TODO: Get cards
        card_images = self.control.get_cropped_images(screenshot, self.CARD_REGIONS)
        cards = []
        for image in card_images:
            cards.append(str.upper(self.card_match.match(image))) #TODO: upper
        print("Hand: ", cards)
        self.merge.update_hand(cards[0], cards[1], cards[2])
        
        #TODO: Get state
        state = self.merge.get_state()
        print("State: ", state)
        
        #TODO: Get agent move 0 - 105
        if random.random() < self.EPSILON:
            action = random.randint(0, self.TOTAL_ACTIONS - 1)
        else:
            with torch.no_grad():
                q_values = self.policy_net(torch.FloatTensor(state))
                action = q_values.argmax().item()
        
        action_name, position = self.decode_action(action)
        print(f"action: {action}, position: {position}")
        row = int(position / 5)
        col = position % 5
        fpoint = self.BOARD[row][col]
        reward = 0
        
        #TODO: Execute move
        if action_name == "buy":
            print("buying: ", position)
            _, reward = self.merge.buy_card(position)
            if position == 0:
                self.control.click(self.HAND[0])
            elif position == 1:
                self.control.click(self.HAND[1])
            else:
                self.control.click(self.HAND[2])
        elif action_name == "sell":
            print("selling: ", row, col)
            _, reward = self.merge.sell_card(row, col)
            self.control.drag(fpoint, self.HAND[0])
        elif action_name == "move_to_front":
            print(f"Moving: {row}{col} to the front!")
            _, r, c, reward = self.merge.move_to_front(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_back":
            print(f"Moving: {row}{col} to the back!")
            _, r, c, reward = self.merge.move_to_back(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_bench":
            print(f"Moving: {row}{col} to the bench!")
            _, r, c, reward = self.merge.move_to_bench(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
        else:
            print("doing nothing")
            
        next_state = self.merge.get_state()
        self.replay_buffer(state, action)
        
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
            return ("no_action", 0)
        
    def recheck_board(self) -> bool:
        for row in range(self.merge.ROWS):
            for col in range(self.merge.COLS):
                prev = self.merge.map[row][col]
                self.control.click(self.BOARD[row][col])
                card_image = pyautogui.screenshot(region=(self.CARD_PICTURE_REGION[0][0] + self.LEFT, self.CARD_PICTURE_REGION[0][1] + self.TOP, (self.CARD_PICTURE_REGION[0][2] - self.CARD_PICTURE_REGION[0][0]), (self.CARD_PICTURE_REGION[0][3] - self.CARD_PICTURE_REGION[0][1])))
                card = self.card_match.match(card_image)
                level_image = pyautogui.screenshot(region=(self.CARD_LEVEL_REGION[0][0], self.CARD_LEVEL_REGION[0][1], self.CARD_LEVEL_REGION[0][2] - self.CARD_LEVEL_REGION[0][0], self.CARD_LEVEL_REGION[0][3] - self.CARD_LEVEL_REGION[0][1]))
                level = self.level_match.match(level_image)
                if prev == 0:
                    if card == 'no_card':
                        #do nothing
                        continue
                    else:
                        #add new card
                        self.merge.add_card_in(str.upper(card), level, row, col)
                        return True
                else:
                    if prev.level == level:
                        #do nothing
                        continue
                    else:
                        #change level TODO: make sure this reference actually changes the object
                        prev.level = level
                        return True
        
        return False
    
    def update_state(self, n_game, n_round, n_move):
        screenshot = self.control.screenshot(filename=f"{n_round}{n_move}screenshot.png", path=f"logs/{n_game}/")
        
        #TODO: Get elixir -> check back on results and do error checking
        elixr_img = self.control.get_cropped_images(screenshot, self.ELIXR_REGION)[0]
        elixr_img.save(f"logs/{n_game}/{n_round}{n_move}elixr.png")
        elixr_img = np.array(elixr_img, dtype=np.uint8)
        results = self.digit_model.predict(source=elixr_img, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        labels = [results.names[int(i)] for i in results.boxes.cls]
        sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
        digits = ''.join(label for label, _ in sorted_detections)
        #TODO: quick fix -> figure out digit model issue
        if len(digits) >= 3:
            elixr = int(digits[0:2])
        else:
            elixr = int(digits)
        print("elixir: ", elixr)
        self.merge.elixir = elixr
        
        #TODO: easy ocr is not cutting it or is it
        max_placement_img = self.control.get_cropped_images(screenshot, self.PLACEMENT_REGION)[0]
        max_placement_img.save(f"logs/{n_game}/{n_round}{n_move}max_placement.png")
        max_placement_img = np.array(max_placement_img, dtype=np.uint8)
        results = self.digit_model.predict(source=max_placement_img, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        labels = [results.names[int(i)] for i in results.boxes.cls]
        sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
        digits = ''.join(label for label, _ in sorted_detections)
        if len(digits) > 0:
            max_placement = int(digits[len(digits) - 1])
            print("max_placement: ", max_placement)
            self.merge.max_placement = max_placement
            
        #TODO: Get cards
        card_images = self.control.get_cropped_images(screenshot, self.CARD_REGIONS)
        cards = []
        for image in card_images:
            cards.append(str.upper(self.card_match.match(image))) #TODO: upper
        print("Hand: ", cards)
        self.merge.update_hand(cards[0], cards[1], cards[2])
        
        return self.merge.get_state()
        
    def do_action(self, action):
        action_name, position = self.decode_action(action)
        print(f"action: {action}, position: {position}")
        row = int(position / 5)
        col = position % 5
        fpoint = self.BOARD[row][col]
        reward = 0
        
        #TODO: Execute move
        if action_name == "buy":
            print("buying: ", position)
            _, reward = self.merge.buy_card(position)
            if position == 0:
                self.control.click(self.HAND[0])
            elif position == 1:
                self.control.click(self.HAND[1])
            else:
                self.control.click(self.HAND[2])
        elif action_name == "sell":
            print("selling: ", row, col)
            _, reward = self.merge.sell_card(row, col)
            self.control.drag(fpoint, self.HAND[0])
        elif action_name == "move_to_front":
            print(f"Moving: {row}{col} to the front!")
            _, r, c, reward = self.merge.move_to_front(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_back":
            print(f"Moving: {row}{col} to the back!")
            _, r, c, reward = self.merge.move_to_back(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_bench":
            print(f"Moving: {row}{col} to the bench!")
            _, r, c, reward = self.merge.move_to_bench(row, col)
            tpoint = self.BOARD[r][c]
            self.control.drag(fpoint, tpoint)
        else:
            print("doing nothing")
            
        return reward
    
    def gold_check(self):
        screenshot = self.control.screenshot()
        
        #Check for golden circles
        gold_results = self.gold_detection.predict(source=screenshot, verbose=False)[0]
        if len(gold_results.boxes) > 0:
            print('Detected gold circle(s)!')
            for box in gold_results.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = box.astype(int)
                x = int((x1 + x2)/2)
                y = int((y1 + y2)/2)
                point = (self.LEFT + x, self.TOP + y)
                print(f'Clicking: x:{x} y:{y}')
                self.control.click(point)
                time.sleep(3)
                self.recheck_board()

                    
        
        
g = Game()
g.train(3)