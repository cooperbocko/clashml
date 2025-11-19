import json
from typing import Tuple
import pyautogui
from merge import Merge
from control import Control
from card_matcher import CardMatch
from text_detect import TextDetect
from image_match import ImageMatch
from dqn import DQN, QTrainer, ReplayBuffer
import numpy as np
from ultralytics import YOLO
import torch
import random
import time
import os

class Game:
    #actions
    NUM_HAND_SLOTS = 3
    NUM_BOARD_SLOTS = 25
    BUY_START = 0
    SELL_START = BUY_START + NUM_HAND_SLOTS
    MOVE_FRONT_START = SELL_START + NUM_BOARD_SLOTS
    MOVE_BACK_START = MOVE_FRONT_START + NUM_BOARD_SLOTS
    MOVE_BENCH_START = MOVE_BACK_START + NUM_BOARD_SLOTS
    NO_ACTION = MOVE_BENCH_START + NUM_BOARD_SLOTS
    TOTAL_ACTIONS = NO_ACTION + 1
    
    #dqn
    EPSILON = 1
    EPSILON_MIN = 0.05
    EPSILON_DECAY = 0.995
    
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.system_settings = self.config["system_settings"]
        self.is_mac_laptop_screen = self.system_settings["is_mac_laptop_screen"]
        
        self.screen_bounds = self.config["screen_bounds"]
        self.left = self.screen_bounds["left"]
        self.top = self.screen_bounds["top"]
        self.right = self.screen_bounds["right"]
        self.bottom = self.screen_bounds["bottom"]
        
        self.regions = self.config["regions"]
        self.card_regions = self.regions["card_regions"]
        self.elixr_region = self.regions["elixr_region"]
        self.placement_region = self.regions["placement_region"]
        self.card_picture_region = self.regions["card_picture_region"]
        self.card_level_region = self.regions["card_level_region"]
        self.defeated_region = self.regions["defeated_region"]
        self.play_again_region = self.regions["play_again_region"]
        self.ok_region = self.regions["ok_region"]
        
        self.click_points = self.config["click_points"]
        self.board = self.click_points["board"]
        self.hand = self.click_points["hand"]
        self.battle = self.click_points["battle"]
        self.safe_click = self.click_points["safe_click"]
        self.end_bar = self.click_points["end_bar"]
        self.play_again = self.click_points["play_again"]
        self.ok = self.click_points["ok"]
        
        self.colors = self.config["colors"]
        self.end_colors = self.colors["end_colors"]
        
        self.merge = Merge()
        self.control = Control(self.left, self.top, self.right, self.bottom) #TODO: make config file give screen size/constatns
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
        best = float('-inf')
        self.control.click(self.battle)
        
        for i in range(n_games - 1):
            if not os.path.isdir(f'logs/{i}'):
                os.mkdir(f'logs/{i}')
            #load time
            time.sleep(10)
            
            run = self.play_game(i)
            if run > best:
                best = run
                self.policy_net.save('./models', 'best_merge.pth')
            self.target_net.load_state_dict(self.policy_net.state_dict())

            self.merge = Merge()
            self.control.click(self.play_again)
            
        last = self.play_game(n_games - 1)
        self.control.click(self.ok)
        if last > best:
            self.policy_net.save('./models', 'best_merge.pth')
        self.policy_net.save('./models', 'last_merge.pth')
        
    def play_game(self, n_game):
        total_reward = 0
        print('Starting game!\n')
        
        print('Getting Starting Card!')
        start1 = self.board[0][2]
        start2 = self.board[3][2]
        self.control.click(start1)
        start_card_image = pyautogui.screenshot(region=(self.card_picture_region[0][0] + self.left, self.card_picture_region[0][1] + self.top, (self.card_picture_region[0][2] - self.card_picture_region[0][0]), (self.card_picture_region[0][3] - self.card_picture_region[0][1])))
        start_card = self.card_match.match(start_card_image)
        if (start_card == 'no_card'):
            self.control.click(start2)
            start_card_image = pyautogui.screenshot(region=(self.card_picture_region[0][0] + self.left, self.card_picture_region[0][1] + self.top, (self.card_picture_region[0][2] - self.card_picture_region[0][0]), (self.card_picture_region[0][3] - self.card_picture_region[0][1])))
            start_card = self.card_match.match(start_card_image)
        self.merge.add_starting_card(str.upper(start_card), 1)
        print('Added: ', start_card)
        print('')
        self.control.click(self.safe_click)
        self.merge.print_map()
        
        print('Entering game loop!\n')
        game_over = False
        game_round = 0
        while not game_over:
            states = []
            actions = []
            rewards = []
            next_states = []
            dones = []
            
            game_round += 1
            move = 0
            state = self.update_state(n_game, game_round, move)
            print(f'----------Round {game_round}-----------------------\n')
            print('Starting Deploy phase!')
            while True: 
                move += 1
                print(f'----------Move {move}-----------------------\n')
                
                #print state:
                self.merge.print_state()
                
                if self.gold_check():
                    state = self.update_state(n_game, game_round, move + 1)
                states.append(state)
                
                if random.random() < self.e:
                    print('random action')
                    action = random.randint(0, self.TOTAL_ACTIONS - 1)
                    self.e = max(self.EPSILON_MIN, self.e * self.EPSILON_DECAY)
                else:
                    with torch.no_grad():
                        print('dqn action')
                        q_values = self.policy_net(torch.FloatTensor(state))
                        action = q_values.argmax().item()
                actions.append(action)
                
                reward, changed = self.do_action(action)
                total_reward += reward
                rewards.append(reward)
                print('reward: ', reward)
                
                if changed:
                    state = self.update_state(n_game, game_round, move)
                else:
                    state = self.merge.get_state()
                next_states.append(state)
                dones.append(False)
                
                end = self.control.check_pixel(self.end_bar, self.is_mac_laptop_screen)
                print("end: ", end)
                if end[0] <= self.end_colors[0] + 20 and end[1] <= self.end_colors[1] + 20 and end[2] <= self.end_colors[2] + 20:
                    break
            
            #transition time
            time.sleep(10)

            print('Starting Battle Phase')
            while True: 
                end = self.control.check_pixel(self.end_bar, self.is_mac_laptop_screen)
                print('end: ', end)
                if end[0] <= self.end_colors[0] + 20 and end[1] <= self.end_colors[1] + 20 and end[2] <= self.end_colors[2] + 20:
                    break
                
                screenshot = self.control.screenshot()
                ok_image = np.array(self.control.get_cropped_images(screenshot, self.ok_region)[0])
                play_again_image = np.array(self.control.get_cropped_images(screenshot, self.play_again_region)[0])
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
                    defeated_image = np.array(self.control.get_cropped_images(screenshot, self.defeated_region)[0])
                    defeated = self.text_detection.detect_text(defeated_image)
                    if len(defeated) > 0:
                        defeated = str.lower(defeated[0])
                    print(defeated)
                    if 'defeated' in defeated:
                        rewards[len(rewards) - 1] -= 30
                        total_reward -= 30
                    else:
                        rewards[len(rewards) - 1] += 30
                        total_reward += 30
                    break
                
                self.trainer.train_step(32)
                time.sleep(1)
                
            self.replay_buffer.push(states, actions, rewards, next_states, dones)
            #round transition time
            time.sleep(7)
        
        print('Game Over!')
        print('Total Reward: ', total_reward)
        return total_reward
        
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
                self.control.click(self.board[row][col])
                card_image = pyautogui.screenshot(region=(self.card_picture_region[0][0] + self.left, self.card_picture_region[0][1] + self.top, (self.card_picture_region[0][2] - self.card_picture_region[0][0]), (self.card_picture_region[0][3] - self.card_picture_region[0][1])))
                card = self.card_match.match(card_image)
                level_image = pyautogui.screenshot(region=(self.card_level_region[0][0], self.card_level_region[0][1], self.card_level_region[0][2] - self.card_level_region[0][0], self.card_level_region[0][3] - self.card_level_region[0][1]))
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
        
        elixr_img = self.control.get_cropped_images(screenshot, self.elixr_region)[0]
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
        self.merge.elixir = elixr
        
        max_placement_img = self.control.get_cropped_images(screenshot, self.placement_region)[0]
        max_placement_img.save(f"logs/{n_game}/{n_round}{n_move}max_placement.png")
        max_placement_img = np.array(max_placement_img, dtype=np.uint8)
        results = self.digit_model.predict(source=max_placement_img, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        labels = [results.names[int(i)] for i in results.boxes.cls]
        sorted_detections = sorted(zip(labels, boxes), key=lambda x: x[1][0])
        digits = ''.join(label for label, _ in sorted_detections)
        if len(digits) > 0:
            max_placement = int(digits[len(digits) - 1])
            self.merge.max_placement = max_placement
            
        card_images = self.control.get_cropped_images(screenshot, self.card_regions)
        cards = []
        for image in card_images:
            cards.append(str.upper(self.card_match.match(image)))
        self.merge.update_hand(cards[0], cards[1], cards[2])
        
        return self.merge.get_state()
        
    def do_action(self, action) -> Tuple[int, bool]:
        action_name, position = self.decode_action(action)
        row = int(position / 5)
        col = position % 5
        fpoint = self.board[row][col]
        reward = 0
        valid = True
        changed = True
        
        if action_name == "buy":
            print("buying: ", position)
            valid, reward = self.merge.buy_card(position)
            changed = valid
            
            if valid:
                if position == 0:
                    self.control.click(self.hand[0])
                elif position == 1:
                    self.control.click(self.hand[1])
                else:
                    self.control.click(self.hand[2])
        elif action_name == "sell":
            print("selling: ", row, col)
            valid, reward = self.merge.sell_card(row, col)
            changed = valid
            
            if valid:
                self.control.drag(fpoint, self.hand[0])
        elif action_name == "move_to_front":
            print(f"Moving: {row}{col} to the front!")
            valid, r, c, reward = self.merge.move_to_front(row, col)
            changed = False
            tpoint = self.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_back":
            print(f"Moving: {row}{col} to the back!")
            valid, r, c, reward = self.merge.move_to_back(row, col)
            changed = False
            tpoint = self.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_bench":
            print(f"Moving: {row}{col} to the bench!")
            valid, r, c, reward = self.merge.move_to_bench(row, col)
            changed = False
            tpoint = self.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        else:
            print("doing nothing")
            
        return (reward, changed)
    
    def gold_check(self):
        screenshot = self.control.screenshot()
        
        gold_results = self.gold_detection.predict(source=screenshot, verbose=False)[0]
        if len(gold_results.boxes) > 0:
            print('Detected gold circle(s)!')
            for box in gold_results.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = box.astype(int)
                x = int((x1 + x2)/2)
                y = int((y1 + y2)/2)
                point = (self.left + x, self.top + y)
                print(f'Clicking: x:{x} y:{y}')
                self.control.click(point)
                time.sleep(3)
                self.recheck_board()
            return True
        return False
                  
g = Game("./configs/mac_config.json")
g.train(3)