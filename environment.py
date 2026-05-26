import time
import random

import numpy as np

from control import Control
from config import Config
from template import TemplateMatch
from image_match import ImageMatch
from merge import Merge
from digits import DetectDigits
from gold import DetectGold
from text_detect import TextDetect

class MergeEnv:
    def __init__(self, config: Config, device):
        self.config = config
        self.control = Control(
            self.config.screen_bounds.left, 
            self.config.screen_bounds.top, 
            self.config.screen_bounds.right, 
            self.config.screen_bounds.bottom,
            0.1
        )
        self.merge = Merge()
        self.game_state = ''
        self.card_match = ImageMatch("models/card_match_db.npz", "images/cards", (56, 70), True, device) 
        self.phase_check = TemplateMatch(0.6, './images/phase')
        self.digit_model = DetectDigits(self.config.system_settings.digit_model, self.config.system_settings.env_path)
        self.gold_model = DetectGold(self.config.system_settings.gold_model, self.config.system_settings.env_path)
        self.text_detect = TextDetect()
        
    def reset(self) -> tuple[np.array, np.array]:
        self.merge = Merge()
        time.sleep(5)
        for i in range(20):
            self.control.click(self.config.click_points.menu_safe_click)
        self.control.click(self.config.click_points.battle)
        
        #Wait for phase icon to appear
        while not self.phase_wait():
            time.sleep(0.5)
        time.sleep(2)
        self.game_state = 'unchecked round'
            
        #Get inital state
        self.get_start_card()
        self.update_state()
        
        return self.merge.get_state()
    
    def step(self, action: int) -> tuple[float, np.array, np.array, bool]:
        #Random check
        if random.random() < 0.1:
            self.update_state(check_elixir=True)
            
        #Enter actual gameplay
        if self.game_state == 'unchecked round':
            #self.gold_check()
            self.update_state(check_elixir=True)
            self.game_state = 'checked round'
            
        prev_value = self.merge.get_value()
        value, changed = self.do_action(action)
        reward = value - prev_value
        new_state, new_mask = self.merge.get_state()
        
        if changed:
            self.update_state(check_elixir=False)
        if not self.check_end():
            return (reward, new_state, new_mask, False)
        
        #Wait for phase to change
        while self.phase_wait():
            time.sleep(1)
        
        #Battle Phase
        while not self.phase_wait():
            screenshot = self.control.screenshot()
            ok_img = self.control.get_cropped_image(
                screenshot,
                self.config.regions.ok_region
            )
            play_again_img = self.control.get_cropped_image(
                screenshot,
                self.config.regions.play_again_region
            )
            ok = self.text_detect.detect_text(ok_img)
            play_again = self.text_detect.detect_text(play_again_img)
            
            if len(play_again) > 0 and len(play_again[0]) > 4:
                time.sleep(5)
                screenshot = self.control.screenshot()
                defeated_img = self.control.get_cropped_image(
                    screenshot,
                    self.config.regions.defeated_region
                )
                defeated = self.text_detect.detect_text(defeated_img)
                if len(defeated) > 0:
                    defeated = str.lower(defeated[0])
                if 'defeated' in defeated:
                    reward += -30
                else:
                    reward += 30
                #Game over
                self.control.click(self.config.click_points.ok)
                return (reward, new_state, new_mask, True)
        #Round over
        if self.merge.max_placement < 6:
            self.merge.max_placement += 1
        self.merge.round += 1
        self.game_state = 'unchecked round'
        return (reward, new_state, new_mask, False)
            
    def phase_wait(self) -> bool:
        screenshot = self.control.screenshot()
        phase = self.control.get_cropped_image(screenshot, self.config.regions.phase_region)

        if self.phase_check.detect(phase):
            return True
        return False
    
    def get_start_card(self):
        start1 = self.config.click_points.board[0][2]
        start2 = self.config.click_points.board[3][2]
        start_card = 'no_card'
        
        while start_card == 'no_card':
            self.control.click(start1)
            start_card_image = self.control.get_cropped_image(
                self.control.screenshot(), 
                self.config.regions.card_picture_region
            )
            start_card = self.card_match.match(start_card_image)
            if (start_card == 'no_card'):
                self.control.click(start2)
                start_card_image = self.control.get_cropped_image(
                    self.control.screenshot(), 
                    self.config.regions.card_picture_region
                )
                start_card = self.card_match.match(start_card_image)
                
        level_image = self.control.get_cropped_image(
            self.control.screenshot(),
            self.config.regions.card_level_region
        )
        #TODO: Make a model for card level
        #start_card_level = int(self.level_match.match(level_image))
        self.merge.add_starting_card(str.upper(start_card), 1)
        self.control.click(self.config.click_points.safe_click)
        
    def update_state(self, check_elixir: bool = True) -> tuple[int, list[str]]:
        screenshot = self.control.screenshot()
        
        elixir = 0
        if check_elixir:
            elixir_img = self.control.get_cropped_image(screenshot, self.config.regions.elixr_region)
            elixir = self.digit_model.predict(elixir_img)
            if len(elixir) > 0:
                self.merge.elixir = int(elixir)
            else:
                self.merge.elixir = 0
        else:
            elixir = self.merge.elixir
            
        cards = []
        card_imgs= []
        for region in self.config.regions.card_regions:
            card_img = self.control.get_cropped_image(screenshot, region)
            card_imgs.append(card_img)
            card = self.card_match.match(card_img)
            cards.append(card)
        self.merge.update_hand(cards[0], cards[1], cards[2])
            
    def gold_check(self):
        screenshot = self.control.fast_screenshot()
        detected, points = self.gold_model.predict(screenshot)
        
        if detected:
            print('Gold Detected!')
            for point in points:
                self.control.click(point)
                
                #Check if gold actually went away
                check_screenshot = self.control.fast_screenshot()
                check_detected, check_points = self.gold_model.predict(check_screenshot)
                if len(check_points) < len(points):
                    self.recheck_board()
    
    def recheck_board(self):
        start = time.time()
        click_time = 0
        screenshot_time = 0
        match_time = 0
        
        points = self.merge.points_to_check()
        for point in points:
            row = point[0]
            col = point[1]
            
            previous = self.merge.map[row][col]
                
            temp = time.time()
            self.control.click(self.config.click_points.board[row][col])
            click_time += time.time() - temp
                
            temp = time.time()
            screenshot = self.control.fast_screenshot()
            screenshot_time += time.time() - temp
                
            temp = time.time()
            current = self.card_match.match(self.control.get_cropped_image(
                screenshot,
                self.config.regions.card_picture_region
            ))
            match_time += time.time() - temp
                
            if current == 'no_card' and previous != 0:
                self.merge.remove_card(row, col)
            else:
                #get level
                level = 1
                if current != 'no_card' and previous == 0:
                    self.merge.add_card_in(str.upper(current), level, row, col)
                elif current != 'no_card' and previous != 0 and previous.level != level:
                    previous.level = level
                        
            temp = time.time()
            self.control.click(self.config.click_points.safe_click)
            click_time += time.time() - temp
                
        print(f"click: {click_time}, screenshot: {screenshot_time}, match: {match_time}, total: {time.time() - start}")
        
    def decode_action(self, action: int) -> tuple[str, int]:
        # action, row, col, row, col
        if 0 <= action <= 2:
            return ("buy", action, 0, 0, 0)
        elif 3 <= action <= 27:
            r = (action - 3) // 5
            c = (action - 3) % 5
            return ("sell", r, c, 0, 0)
        elif 28 <= action <= 652:
            from_r = ((action - 28) // 25) // 5
            from_c = ((action - 28) // 25) % 5
            to_r = ((action - 28) % 25) // 5
            to_c = ((action - 28) % 25) % 5
            return ("move", from_r, from_c, to_r, to_c)
        else:
            return ("no_action", action, 0, 0, 0)

    def do_action(self, action: int) -> tuple[int, bool]:
        action_name, row, col, to_row, to_col = self.decode_action(action)
        changed = True
        
        if action_name == "buy":
            if row == 0:
                self.control.click(self.config.click_points.hand[0])
            elif row == 1:
                self.control.click(self.config.click_points.hand[1])
            else:
                self.control.click(self.config.click_points.hand[2])
            self.merge.buy_card(row)
        elif action_name == "sell":
            self.control.drag(self.config.click_points.board[row][col], self.config.click_points.hand[0])
            self.merge.sell_card(row, col)
        elif action_name == "move":
            fpoint = self.config.click_points.board[row][col]
            tpoint = self.config.click_points.board[to_row][to_col]
            self.control.drag(fpoint, tpoint)
            self.merge.move_card(row, col, to_row, to_col)
            changed = False
        else:
            changed = False
            
        return (self.merge.get_value(), changed)
    
    def check_end(self) -> bool:
        end = self.control.check_pixel(self.config.click_points.end_bar, self.config.system_settings.is_mac_laptop_screen)
                    
        if (end[0] <= self.config.colors.end_colors[0] + 20 and 
            end[1] <= self.config.colors.end_colors[1] + 20 and
            end[2] <= self.config.colors.end_colors[2] + 20):
            return True
        else:
            return False
        
    def get_state(self) -> list[int]:
        return self.merge.get_state()
    