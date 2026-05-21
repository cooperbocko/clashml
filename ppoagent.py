import time

import numpy as np
import torch

from environment import MergeEnv
from config import Config
from ppo import ActorCritic, ReplayBuffer, PPOTrainer, GameState, Experience

class PPOAgent:
    def __init__(self, config_path: str, debug: bool = True):
        if torch.cuda.is_available():
            print("Using CUDA GPU")
            self.device = torch.device("cuda")
        else:
            print("CUDA GPU not available, using CPU")
            self.device = torch.device("cpu")
        self.config = Config.load_from_json(config_path)
        self.env = MergeEnv(self.config, self.device)
        self.model = ActorCritic(n_cards = self.env.merge.N_CARDS, n_syns = self.env.merge.N_SYNS, n_stats= 4)
        self.replay_buffer = ReplayBuffer(capacity=10)
        self.trainer = PPOTrainer(self.model, self.replay_buffer, torch.optim.Adam(self.model.parameters(), lr=1e-3), clip_param=0.2, epochs=10, batch_size=32, value_loss_coef=0.5, entropy_coef=0.01)
        
    def train(self, n_games: int):
        for i in range(n_games):
            game_state, action_mask = self.env.reset()
            action, value, log_prob, hidden = self.get_action(GameState(**game_state), None, action_mask)
            episode = []
            old_experience = None
            self.env.merge.print_map()
            
            while True:
                time.sleep(0.1)
                reward, next_game_state, next_action_mask, done = self.env.step(action)
                self.env.merge.print_map()
                self.trainer.train(1, 16)
                
                experience = Experience(
                    state = game_state,
                    action = action,
                    reward = reward,
                    done = done,
                    log_prob = log_prob,
                    value = value,
                    next_value = None,
                    hidden = hidden
                )
                
                if old_experience:
                    old_experience.next_value = value
                    episode.append(old_experience)
                
                old_experience = experience
                game_state, action_mask = next_game_state, next_action_mask
                action, value, log_prob, hidden = self.get_action(GameState(**game_state), hidden, next_action_mask)
                if done:
                    break
            
            if old_experience:
                episode.append(old_experience)
            if len(episode) > 0:
                self.replay_buffer.push_experience(episode)
                
            #save, summary
            self.model.save('./models/', f'model_{i}.pth')
                
    def get_action(self, state: GameState, hidden, mask: np.array) -> tuple[int, torch.Tensor]:
        logits, value, hidden = self.model(state.board_cards, state.board_pos, state.shop_cards, state.game_data, hidden)
        
        masked_logits = torch.where(mask.bool(), torch.tensor(float('-inf')), logits, device=self.device)
        dist = torch.distributions.Categorical(logits=masked_logits)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        
        return (action, value, log_prob, hidden)