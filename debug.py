import os
from PIL import Image

class Debug():
    def __init__(self):
        self.nstep = 0
        self.bmap = ''
        self.amap = ''
        self.elixir = 0
        self.cards = []
        self.action = ''
        self.reward = 0
        
    def print_step(self):
        print(f'step {self.nstep} --------------------')
        print('Before Map:')
        print(self.bmap)
        print(f'Action:{self.action}')
        print(f'Reward:{self.reward}')
        print(f"Elixir:{self.elixir}")
        print(f"hand:{self.cards}")
        print('After Map:')
        print(self.amap)
        
        self.nstep += 1
        self.bmap = self.amap
        
    def save_image(self, image: Image, thing: str):
        dir_path = f"debug/{self.nstep}"
        os.makedirs(dir_path, exist_ok=True)

        file_name = f"{thing}_{self.nstep}.png"
        image.save(os.path.join(dir_path, file_name))
        
    