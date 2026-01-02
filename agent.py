import json
import random
import time
from typing import Tuple
from datetime import datetime

import cv2
import numpy as np
import torch
import pyautogui

from edge import DetectEdge
from merge import Merge
from control import Control
from text_detect import TextDetect
from image_match import ImageMatch
from dqn import DQN, QTrainer, ReplayBuffer
from debug import Debug
from digits import DetectDigits
from template import TemplateMatch
from gold import DetectGold

class Agent:
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
    
    def __init__(self, config_path: str, debug: bool = False):
        if torch.cuda.is_available():
            print("Using CUDA GPU")
            device = torch.device("cuda")
        else:
            print("CUDA GPU not available, using CPU")
            device = torch.device("cpu")

        self.debug_mode = debug
        
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.system_settings = self.config["system_settings"]
        self.is_mac_laptop_screen = self.system_settings["is_mac_laptop_screen"]
        self.env_path = self.system_settings["env_path"]
        self.is_roboflow = self.system_settings["is_roboflow"]
        self.verbose = False

        self.game_start_delay = 3
        self.click_delay = 0.1
        self.action_delay = 0.1
        self.state_update_delay = 0.5
        self.phase_transition_delay = 1
        self.end_delay = 3
        
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
        self.phase_region = self.regions["phase_region"]
        
        self.click_points = self.config["click_points"]
        self.board = self.click_points["board"]
        self.hand = self.click_points["hand"]
        self.battle = self.click_points["battle"]
        self.safe_click = self.click_points["safe_click"]
        self.menu_safe_click = self.click_points['menu_safe_click']
        self.end_bar = self.click_points["end_bar"]
        self.play_again = self.click_points["play_again"]
        self.ok = self.click_points["ok"]
        
        self.colors = self.config["colors"]
        self.end_colors = self.colors["end_colors"]
        
        self.merge = Merge()
        self.debug = Debug(self.merge)
        self.control = Control(self.left, self.top, self.right, self.bottom, self.click_delay)
        self.card_match = ImageMatch("models/card_match_db.npz", "images/cards", (56, 70), True) 
        self.level_match = ImageMatch("models/level_match_db.npz", "images/levels", (19, 18), False)
        self.text_detection = TextDetect()
        self.digit_model = DetectDigits(self.is_roboflow, "models/best_digits.pt", self.env_path)
        self.gold_detection = DetectGold(True, "models/best_gold.pt", self.env_path)
        self.policy_net = DQN(len(self.merge.get_state()), 128, self.TOTAL_ACTIONS)
        #self.policy_net.load('./models/100_last.pth') -> use this to load pretained weights
        self.target_net = DQN(len(self.merge.get_state()), 128, self.TOTAL_ACTIONS)
        self.replay_buffer = ReplayBuffer(capacity=100000)
        self.trainer = QTrainer(self.policy_net, self.target_net, self.replay_buffer, 1e-3, 0.99)
        self.e = self.EPSILON
        self.phase_check = TemplateMatch(0.6, ['./images/phase'])
        self.edge_detect = DetectEdge(self.control, self.board, 5, 5)
        
    def train(self, n_games: int):
        best = float('-inf')

        for i in range(n_games):
            self.control.click(self.battle)
            print(f'Playing game {i}')
                
            while True:
                screenshot = self.control.screenshot()
                phase = self.control.get_cropped_images(screenshot, self.phase_region)[0]
                if self.phase_check.detect(phase):
                    time.sleep(self.game_start_delay)
                    break

                if self.debug_mode:
                    self.debug.save_image(phase, 'phase', 'pre')
                
            run = self.play_game()
            self.merge = Merge()
            if run > best:
                best = run
                self.policy_net.save('./models', 'best_merge.pth')
                self.target_net.load_state_dict(self.policy_net.state_dict())
                
            if self.debug_mode:
                self.debug.print_game()
                self.debug.merge = self.merge
                
            self.policy_net.save('./models', 'last_merge.pth')

            self.control.click(self.ok)
            for i in range(10):
                self.control.click(self.menu_safe_click)

    def play_game(self) -> float:
        total_reward = 0
        if self.debug_mode:
            print('Starting game!\n')
        
        self.get_start_card()

        game_over = False
        while not game_over:
            states, actions, rewards, next_states, dones = self.deploy_phase()

            while True:
                screenshot = self.control.screenshot()
                phase = self.control.get_cropped_images(screenshot, self.phase_region)[0]
                if not self.phase_check.detect(phase):
                    time.sleep(self.phase_transition_delay)
                    break
            if self.debug_mode:
                print('Starting Battle Phase')
                
            rewards, dones, game_over = self.battle_phase(rewards, dones)
            self.replay_buffer.push(states, actions, rewards, next_states, dones)

            if self.merge.max_placement < 6:
                self.merge.max_placement += 1
            
            if self.debug_mode:
                self.debug.print_round()
        
        if self.debug_mode:
            self.debug.total_reward = total_reward
            
        return total_reward
    
    def get_start_card(self):
        start1 = self.board[0][2]
        start2 = self.board[3][2]
        start_card = 'no_card'
        while start_card == 'no_card':
            self.control.click(start1)
            start_card_image = pyautogui.screenshot(region=(self.card_picture_region[0][0] + self.left, self.card_picture_region[0][1] + self.top, (self.card_picture_region[0][2] - self.card_picture_region[0][0]), (self.card_picture_region[0][3] - self.card_picture_region[0][1])))
            start_card = self.card_match.match(start_card_image)
            if (start_card == 'no_card'):
                self.control.click(start2)
                start_card_image = pyautogui.screenshot(region=(self.card_picture_region[0][0] + self.left, self.card_picture_region[0][1] + self.top, (self.card_picture_region[0][2] - self.card_picture_region[0][0]), (self.card_picture_region[0][3] - self.card_picture_region[0][1])))
                start_card = self.card_match.match(start_card_image)
        level_image = pyautogui.screenshot(region=(self.card_level_region[0][0] + self.left, self.card_level_region[0][1] + self.top, (self.card_level_region[0][2] - self.card_level_region[0][0]), (self.card_level_region[0][3] - self.card_level_region[0][1])))
        start_card_level = int(self.level_match.match(level_image))
        self.merge.add_starting_card(str.upper(start_card), start_card_level)
        self.control.click(self.safe_click)
        
        if self.debug_mode:
            print('Added: ', start_card)
            print('At level: ', start_card_level)
            print('Entering game loop!\n')
            print('Inital game map')
            self.merge.print_map()
            self.debug.save_image(start_card_image, 'startcard', 'start')
            self.debug.save_image(level_image, 'level', 'start')

    def deploy_phase(self):
        states = []
        actions = []
        rewards = []
        next_states = []
        dones = []
        state = []
            
        if self.debug_mode:
            print('Starting Deploy phase!')
                
        self.gold_check()
        state = self.update_state()
                
        while True: 
            states.append(state)
                
            if random.random() < self.e:
                action = random.randint(0, self.TOTAL_ACTIONS - 1)
                self.e = max(self.EPSILON_MIN, self.e * self.EPSILON_DECAY)
                    
                if self.debug_mode:
                    self.debug.random_action = True
            else:
                with torch.no_grad():
                    q_values = self.policy_net(torch.FloatTensor(state))
                    action = q_values.argmax().item()
                        
                if self.debug_mode:
                    self.debug.random_action = False
            actions.append(action)
                
            reward, changed = self.do_action(action)
            total_reward += reward
            rewards.append(reward)
                
            if changed:
                time.sleep(self.state_update_delay)
                state = self.update_state()
            else:
                state = self.merge.get_state()
            next_states.append(state)
            dones.append(False)
            
            self.trainer.train_step(32)

            if self.debug_mode:
                self.debug.print_step()
                
            if self.check_end():
                return (states, actions, rewards, next_states, dones)
            
    def battle_phase(self, rewards, dones):
        while True: 
            screenshot = self.control.screenshot()
                
            phase = self.control.get_cropped_images(screenshot, self.phase_region)[0]
            if self.phase_check.detect(phase):
                time.sleep(self.phase_transition_delay)
                break
                
            ok_image = np.array(self.control.get_cropped_images(screenshot, self.ok_region)[0])
            play_again_image = np.array(self.control.get_cropped_images(screenshot, self.play_again_region)[0])
            ok = self.text_detection.detect_text(ok_image)
            play_again = self.text_detection.detect_text(play_again_image)
                        
            if len(play_again) > 0 and len(play_again[0]) > 4:
                game_over = True
                dones[len(dones) - 1] = True
                time.sleep(self.end_delay)
                    
                screenshot = self.control.screenshot()
                defeated_image = np.array(self.control.get_cropped_images(screenshot, self.defeated_region)[0])
                defeated = self.text_detection.detect_text(defeated_image)
                if len(defeated) > 0:
                    defeated = str.lower(defeated[0])
                    
                if 'defeated' in defeated:
                    rewards[len(rewards) - 1] -= 30
                    total_reward -= 30
                else:
                    rewards[len(rewards) - 1] += 30
                    total_reward += 30
                        
                if self.debug_mode:
                    print(f'ok: {ok}')
                    print(f'play_again: {play_again}')
                    print(f'defeated: {defeated}')
                    self.debug.save_image(screenshot, 'screenshot', 'end')
                
                return (rewards, dones, game_over)
                
            self.trainer.train_step(32)
        
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
        
    def do_action(self, action: int) -> Tuple[int, bool]:
        action_name, position = self.decode_action(action)
        row = int(position / 5)
        col = position % 5
        fpoint = self.board[row][col]
        reward = 0
        valid = True
        changed = True
        
        if action_name == "buy":
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
            valid, reward = self.merge.sell_card(row, col)
            changed = valid
            
            if valid:
                self.control.drag(fpoint, self.hand[0])
        elif action_name == "move_to_front":
            valid, r, c, reward = self.merge.move_to_front(row, col)
            changed = False
            tpoint = self.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_back":
            valid, r, c, reward = self.merge.move_to_back(row, col)
            changed = False
            tpoint = self.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_bench":
            valid, r, c, reward = self.merge.move_to_bench(row, col)
            changed = False
            tpoint = self.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        else:
            changed = False
                
        if self.debug_mode:
            self.debug.action = action_name
            self.debug.position = (row, col)
            self.debug.reward = reward
            self.debug.changed = changed
            
        if valid:
            time.sleep(self.action_delay)
        return (reward, changed)
    
    def update_state(self):
        screenshot = self.control.screenshot()
        elixr = 0
        
        start = datetime.now()
        elixr_img = self.control.get_cropped_images(screenshot, self.elixr_region)[0]
        elixr = self.digit_model.predict(elixr_img)
        if len(elixr) > 0:
            self.merge.elixir = int(elixr)
        else:
            self.merge.elixir = 0
        elapsed = (datetime.now() - start).total_seconds()
        print(f'elixr update: f{elapsed}')
        
        '''
        start = datetime.now()
        max_placement_img = self.control.get_cropped_images(screenshot, self.placement_region)[0]
        max_placement = self.digit_model.predict(max_placement_img)
        if len(max_placement) > 0:
            max_placement = max_placement[len(max_placement)-1]
            if (int(max_placement)) >= self.merge.max_placement:
                self.merge.max_placement = int(max_placement)
        elapsed = (datetime.now() - start).total_seconds()
        print(f'placement update: f{elapsed}')
        '''
        
        start = datetime.now()
        card_images = self.control.get_cropped_images(screenshot, self.card_regions)
        cards = []
        for image in card_images:
            cards.append(str.upper(self.card_match.match(image)))
        self.merge.update_hand(cards[0], cards[1], cards[2])
        elapsed = (datetime.now() - start).total_seconds()
        print(f'cards update: f{elapsed}')
        
        if self.debug_mode:
            self.debug.save_image(screenshot, 'screenshot', 'battle')
            self.debug.save_image(elixr_img, 'elixr', 'battle')
            #self.debug.save_image(max_placement_img, 'placement', 'battle')
            for card_image in card_images:
                self.debug.save_image(card_image, 'cards', 'battle')
            self.debug.elixr = elixr
            #self.debug.max_placement = max_placement
            self.debug.cards = cards
        
        return self.merge.get_state()
    
    def gold_check(self):
        screenshot = self.control.screenshot()
        
        detected, points = self.gold_detection.predict(screenshot)
        if detected:
            print('Gold Detected!')
            for point in points:
                self.control.click(point)
            self.recheck_board()
            return True
        return False
        
    def recheck_board(self) -> bool:
        screen = self.control.screenshot()
        onboard = self.edge_detect.detect_edges(screen)
        
        for row in range(self.merge.ROWS):
            for col in range(self.merge.COLS):
                prev = self.merge.map[row][col]
                curr = onboard[row][col]
                
                #If previous board was empty and current board is empty, go to next position
                if prev == 0 and curr == 0:
                    continue
                
                self.control.click(self.board[row][col])
                card_image = pyautogui.screenshot(region=(self.card_picture_region[0][0] + self.left, self.card_picture_region[0][1] + self.top, (self.card_picture_region[0][2] - self.card_picture_region[0][0]), (self.card_picture_region[0][3] - self.card_picture_region[0][1])))
                card = self.card_match.match(card_image)
                level_image = pyautogui.screenshot(region=(self.card_level_region[0][0], self.card_level_region[0][1], self.card_level_region[0][2] - self.card_level_region[0][0], self.card_level_region[0][3] - self.card_level_region[0][1]))
                level = int(self.level_match.match(level_image))
                
                if self.debug_mode:
                    self.debug.save_image(level_image, 'level', 'gold_check')
                
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
        
    def check_end(self):
        end = self.control.check_pixel(self.end_bar, self.is_mac_laptop_screen)
        if self.debug_mode:
            self.debug.end = end
                    
        if end[0] <= self.end_colors[0] + 20 and end[1] <= self.end_colors[1] + 20 and end[2] <= self.end_colors[2] + 20:
            return True
        else:
            return False