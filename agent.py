import random
import time

import torch

from config import Config
from environment import MergeEnv
from dqn import DQN, QTrainer, ReplayBuffer

class Agent:
    #dqn
    EPSILON = 1
    EPSILON_MIN = 0.05
    EPSILON_DECAY = 0.995
    
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
    
    def __init__(self, config_path: str, env_path: str, debug: bool = False):
        if torch.cuda.is_available():
            print("Using CUDA GPU")
            device = torch.device("cuda")
        else:
            print("CUDA GPU not available, using CPU")
            device = torch.device("cpu")
        self.config = Config.load_from_json(config_path)
        self.env = MergeEnv(self.config, env_path)
        self.policy_net = DQN(len(self.env.get_state()), 128, self.TOTAL_ACTIONS)
        #self.policy_net.load('./models/100_last.pth') -> use this to load pretained weights
        self.target_net = DQN(len(self.env.get_state()), 128, self.TOTAL_ACTIONS)
        self.replay_buffer = ReplayBuffer(capacity=100000)
        self.trainer = QTrainer(self.policy_net, self.target_net, self.replay_buffer, 1e-3, 0.99)
        self.e = self.EPSILON
        
    def train(self, n_games: int):
        best = float('-inf')
        
        for i in range(n_games):
            #inital state
            run = 0
            state = self.env.reset()
            action = self.get_action(state)
            game_reward = 0
            
            #play game
            while True:
                time.sleep(0.25)
                prev_state, action, reward, next_state, done = self.env.step(action)
                game_reward += reward
                self.replay_buffer.push(prev_state, action, reward, next_state, done)
                self.trainer.train_step(32)
                if done:
                    break
                action = self.get_action(next_state)
            
            #summary, statistics, saves
            if run > best:
                best = run
                self.policy_net.save('./models', 'best_merge.pth')
                self.target_net.load_state_dict(self.policy_net.state_dict())
            self.policy_net.save('./models', 'last_merge.pth')
            
    def get_action(self, state: list[int]):
        action = 0
        if random.random() < self.e:
                half = random.randint(0, 1)
                if 0.5 >= half:
                    action = random.randint(0, 2)
                else:
                    action = random.randint(0, self.TOTAL_ACTIONS - 1)
                self.e = max(self.EPSILON_MIN, self.e * self.EPSILON_DECAY)
        else:
            with torch.no_grad():
                q_values = self.policy_net(torch.FloatTensor(state))
                action = q_values.argmax().item()
            self.e = max(self.EPSILON_MIN, self.e * self.EPSILON_DECAY)
        return action