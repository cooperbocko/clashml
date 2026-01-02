import os
from merge import Merge
from PIL import Image


class Debug():
    def __init__(self, merge: Merge, path: str='debug', verbose: bool=False):
        self.merge = merge
        self.path = path
        self.verbose = verbose
        self.ngame = 0
        self.nround = 0
        self.nstep = 0
        self.action = ''
        self.position = (0 ,0)
        self.reward = 0
        self.total_reward = 0
        self.random_action = True
        self.elixr = 0
        self.max_placement = 0
        self.cards = []
        self.end = ()
        self.changed = False
        
    def print_step(self):
        if not self.verbose and not self.changed:
            self.nstep += 1
            return
        
        self.print_step_line()
        print(f'elixr detected: {self.elixr} elixr in merge: {self.merge.elixir}')
        print(f'max_placement detected: {self.max_placement} max_placement in merge: {self.merge.max_placement}')
        print(f'cards: {self.cards}')
        if self.random_action:
            print(f'random action: {self.action} at row: {self.position[0]} col: {self.position[1]}')
        else:
            print(f'dqn action: {self.action} at row: {self.position[0]} col: {self.position[1]}')
        print(f'reward: {self.reward}')
        print('map after action: ')
        self.merge.print_map()
        self.nstep += 1
        
    def print_round(self):
        self.print_round_line()
        print(f'round summary: ')
        print(f'# of steps: {self.nstep}')
        self.nround += 1
        self.nstep = 0
        
    def print_game(self):
        self.print_game_line()
        print(f'game summary: ')
        print(f'# of rounds: {self.nround}')
        print(f'total reward: {self.total_reward}')
        self.nround = 0
        self.ngame += 1
        
    def save_image(self, image: Image, thing: str, phase: str):
        dir_path = f"debug/{self.ngame}/{self.nround}/{phase}"
        os.makedirs(dir_path, exist_ok=True)

        file_name = f"{thing}_{self.nstep}.png"
        image.save(os.path.join(dir_path, file_name))
        
    def print_divider(self, text):
        print(f'--------------- {text} ---------------')
        
    def print_step_line(self):
        text = f'step: {self.nstep}'
        self.print_divider(text)
        
    def print_round_line(self):
        text = f'round: {self.nround}'
        self.print_divider(text)
        
    def print_game_line(self):
        text = f'game: {self.ngame}'
        self.print_divider(text)