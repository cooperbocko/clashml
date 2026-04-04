from environment import MergeEnv
from config import Config
import torch
import time

config = Config.load_from_json('./configs/mac.json')
device = torch.device("cpu")
env = MergeEnv(config, device)


while True:
    key = input("Press a key to take a screen shot: ")
    time.sleep(3)
    print(env.merge.print_map())
    env.recheck_board()
    print(env.merge.print_map())
    


    


