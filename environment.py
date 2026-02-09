import time

from control import Control
from config import Config
from template import TemplateMatch
from image_match import ImageMatch
from merge import Merge
from digits import DetectDigits
from gold import DetectGold
from edge import DetectEdge
from text_detect import TextDetect
from debug import Debug

class MergeEnv:
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
    
    def __init__(self, config: Config, env_path: str):
        self.config = config
        self.debug = Debug()
        self.debug_mode = True
        self.control = Control(
            self.config.screen_bounds.left, 
            self.config.screen_bounds.top, 
            self.config.screen_bounds.right, 
            self.config.screen_bounds.bottom,
            0.1
        )
        self.merge = Merge()
        self.game_state = ''
        self.card_match = ImageMatch("models/card_match_db.npz", "images/cards", (56, 70), True) 
        self.level_match = ImageMatch("models/level_match_db.npz", "images/levels", (19, 18), False)
        self.phase_check = TemplateMatch(0.6, './images/phase')
        self.digit_model = DetectDigits(
            self.config.system_settings.is_roboflow,
            './models/best_digits.pt',
            self.config.system_settings.env_path
        )
        self.gold_model = DetectGold(True, "models/best_gold.pt", env_path)
        self.edge_detect = DetectEdge(self.control, self.config.click_points.board, 5, 5)
        self.text_detect = TextDetect()
        
    def reset(self):
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
        
        #Debug
        if self.debug_mode:
            self.debug.bmap = self.merge.print_map()
        
        return self.merge.get_state()
    
    def step(self, action: int) -> tuple[list[int], int, float, list[int], bool]:
        #Enter actual gameplay
        if self.game_state == 'unchecked round':
            #self.gold_check()
            self.update_state()
            self.game_state = 'checked round'
            
        prev_state = self.merge.get_state()
        reward, changed = self.do_action(action)
        #Debug
        if self.debug_mode:
            self.debug.reward = reward
            name, position = self.decode_action(action)
            if name == "buy":
                row = 0
                col = position
            else:
                row = int(position / 5)
                col = position % 5
            self.debug.action = f'{name}:{row}-{col}'
            self.debug.amap = self.merge.print_map()
        if changed:
            time.sleep(0.5)
            self.update_state()
        if not self.check_end():
            #Debug
            if self.debug_mode:
                self.debug.print_step()
            return (prev_state, action, reward, self.merge.get_state(), False)
        
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
                #Debug
                if self.debug_mode:
                    self.debug.reward = reward
                    self.debug.print_step()
                return (prev_state, action, reward, self.merge.get_state(), True)
        #Round over
        if self.merge.max_placement < 6:
            self.merge.max_placement += 1
        self.game_state = 'unchecked round'
        #Debug
        if self.debug_mode:
            self.debug.print_step()
        return (prev_state, action, reward, self.merge.get_state(), False)
            
    def phase_wait(self) -> bool:
        screenshot = self.control.screenshot()
        phase = self.control.get_cropped_image(screenshot, self.config.regions.phase_region)
        #Debug
        if self.debug_mode:
            self.debug.save_image(phase, 'phase')
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
        start_card_level = int(self.level_match.match(level_image))
        self.merge.add_starting_card(str.upper(start_card), start_card_level)
        self.control.click(self.config.click_points.safe_click)
        
        #Debug
        if self.debug_mode:
            self.debug.save_image(start_card_image, 'start_card')
            self.debug.save_image(level_image, 'start_card_level')
        
    def update_state(self) -> tuple[int, list[str]]:
        screenshot = self.control.screenshot()
        
        elixir = 0
        elixir_img = self.control.get_cropped_image(screenshot, self.config.regions.elixr_region)
        elixir = self.digit_model.predict(elixir_img)
        if len(elixir) > 0:
            self.merge.elixir = int(elixir)
        else:
            self.merge.elixir = 0
            
        cards = []
        card_imgs= []
        for region in self.config.regions.card_regions:
            card_img = self.control.get_cropped_image(screenshot, region)
            card_imgs.append(card_img)
            card = self.card_match.match(card_img)
            cards.append(card)
        self.merge.update_hand(cards[0], cards[1], cards[2])
        
        #Debug
        if self.debug_mode:
            self.debug.save_image(screenshot, 'screenshot')
            self.debug.save_image(elixir_img, 'elixir')
            pos = 0
            for card_img in card_imgs:
                pos += 1
                self.debug.save_image(card_img, f'card{pos}')
            self.debug.elixir = elixir
            self.debug.cards = cards
            
    def gold_check(self) -> bool:
        screenshot = self.control.screenshot()
        
        detected, points = self.gold_model.predict(screenshot)
        if detected:
            print('Gold Detected!')
            for point in points:
                self.control.click(point)
            self.recheck_board()
            return True
        return False
    
    def recheck_board(self) -> bool:
        screenshot = self.control.screenshot()
        onboard = self.edge_detect.detect_edges(screenshot)
        
        for row in range(self.merge.ROWS):
            for col in range(self.merge.COLS):
                prev = self.merge.map[row][col]
                curr = onboard[row][col]
                
                #If previous board was empty and current board is empty, go to next position
                if prev == 0 and curr == 0:
                    continue
                
                self.control.click(self.config.click_points.board[row][col])
                screenshot = self.control.screenshot()
                card_image = self.control.get_cropped_image(
                    screenshot,
                    self.config.regions.card_picture_region
                )
                card = self.card_match.match(card_image)
                level_image = self.control.get_cropped_image(
                    screenshot,
                    self.config.regions.card_level_region
                )
                level = int(self.level_match.match(level_image))
                
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
        
    def do_action(self, action: int) -> tuple[int, bool]:
        action_name, position = self.decode_action(action)
        row = int(position / 5)
        col = position % 5
        fpoint = self.config.click_points.board[row][col]
        reward = 0
        valid = True
        changed = True
        
        if action_name == "buy":
            valid, reward = self.merge.buy_card(position)
            changed = valid
            if valid:
                if position == 0:
                    self.control.click(self.config.click_points.hand[0])
                elif position == 1:
                    self.control.click(self.config.click_points.hand[1])
                else:
                    self.control.click(self.config.click_points.hand[2])
        elif action_name == "sell":
            valid, reward = self.merge.sell_card(row, col)
            changed = valid
            
            if valid:
                self.control.drag(fpoint, self.config.click_points.hand[0])
        elif action_name == "move_to_front":
            valid, r, c, reward = self.merge.move_to_front(row, col)
            changed = False
            tpoint = self.config.click_points.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_back":
            valid, r, c, reward = self.merge.move_to_back(row, col)
            changed = False
            tpoint = self.config.click_points.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        elif action_name == "move_to_bench":
            valid, r, c, reward = self.merge.move_to_bench(row, col)
            changed = False
            tpoint = self.config.click_points.board[r][c]
            
            if valid:
                self.control.drag(fpoint, tpoint)
        else:
            changed = False
            
        return (reward, changed)
    
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
    