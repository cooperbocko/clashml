import random
import os
from tracemalloc import start
from typing import NamedTuple, TypedDict

from regex import E
import torch
import torch.nn as nn
import numpy as np

class GameState(TypedDict):
    board_cards: np.ndarray
    board_pos: np.ndarray
    shop_cards: np.ndarray
    game_data: np.ndarray

class ActorCritic(nn.Module):
    def __init__(self, n_cards, n_syns, n_stats):
        super().__init__()
        self.card_encoder = CardEncoder(n_cards, n_syns, 64, 32)
        self.pos_dim = get_emb_dim(25)
        self.board_encoder = BoardEncoder(self.card_encoder, 25, self.pos_dim)
        self.shop_encoder = ShopEncoder(self.card_encoder)
        self.data_encoder = DataEncoder(n_stats, 64, 32)
        self.lstm = LSTM(32 + self.pos_dim + 32 + 32, 128)
        self.action_heads = ActionHeads(128, 32, self.pos_dim)
        self.critic_head = nn.Linear(128, 1)
        
    def forward(self, board_cards, board_pos, shop_cards, game_data, hidden=None):
        board_summary, board_embs = self.board_encoder(board_cards, board_pos)
        shop_summary, shop_embs = self.shop_encoder(shop_cards)
        data_summary = self.data_encoder(game_data)
        combined = torch.cat([board_summary, shop_summary, data_summary], dim=-1)
        combined = combined.unsqueeze(1)
        
        lstm_out, hidden = self.lstm(combined, hidden)
        logits = self.action_heads(lstm_out, shop_embs, board_embs)
        value = self.critic_head(lstm_out)
        return logits, value, hidden
    
    def save(self, file_path: str, file_name: str):
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        file_name = os.path.join(file_path, file_name)
        torch.save(self.state_dict(), file_name)
        
class ActionHeads(nn.Module):
    def __init__(self, hidden_size, card_dim, pos_dim):
        super().__init__()
        self.buy = nn.Linear(hidden_size, card_dim)
        self.sell = nn.Linear(hidden_size, card_dim + pos_dim)
        self.src_move = nn.Linear(hidden_size, card_dim + pos_dim)
        self.dst_move = nn.Linear(hidden_size, card_dim + pos_dim)
        self.do_nothing = nn.Linear(hidden_size, 1)
        
    def forward(self, lstm_out, shop_cards, board_cards, mask=None):
        buy = self.buy(lstm_out).unsqueeze(-1)
        sell = self.sell(lstm_out).unsqueeze(-1)
        smove = self.src_move(lstm_out).unsqueeze(-1)
        dmove = self.dst_move(lstm_out).unsqueeze(-1)
        
        buy_logits = torch.bmm(shop_cards, buy).squeeze(-1)
        sell_logits = torch.bmm(board_cards, sell).squeeze(-1)
        smove_logits = torch.bmm(board_cards, smove).squeeze(-1)
        dmove_logits = torch.bmm(board_cards, dmove).squeeze(-1)
        move_logits = smove_logits.unsqueeze(2) + dmove_logits.unsqueeze(1)
        move_logits = move_logits.view(lstm_out.size(0), -1)
        nothing_logits = self.do_nothing(lstm_out)
        
        all_logits = torch.cat([buy_logits, sell_logits, move_logits, nothing_logits], dim=-1)
        if mask:
            all_logits = all_logits + (mask * -1e9)
        return all_logits

class LSTM(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(LSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=2, batch_first=True)

    def forward(self, game_states, hidden=None):
        out, hidden = self.lstm(game_states, hidden)
        return out, hidden

# id, syns, level, cost
class CardEncoder(nn.Module):
    def __init__(self, n_cards, n_syns, hidden_size, latent_size):
        super(CardEncoder, self).__init__()
        
        self.id_emb = nn.Embedding(n_cards, get_emb_dim(n_cards))
        self.syn_emb = nn.EmbeddingBag(n_syns, get_emb_dim(n_syns), mode='mean')
        input_size = get_emb_dim(n_cards) + get_emb_dim(n_syns) + 2
        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, latent_size)
        )
    
    def forward(self, card_data):
        id_emb = self.id_emb(card_data[:, 0])
        syn_emb = self.syn_emb(card_data[:, 1:3])
        level = card_data[:, 3].view(-1, 1)
        cost = card_data[:, 4].view(-1, 1)
        x = torch.cat([id_emb, syn_emb, level, cost], dim=1)
        return self.layers(x)
    
class BoardEncoder(nn.Module):
    def __init__(self, card_encoder, n_pos, pos_dim):
        super(BoardEncoder, self).__init__()
        self.card_encoder = card_encoder
        self.pos_emb = nn.Embedding(n_pos, pos_dim)
    
    def forward(self, card_batch, pos_indices):
        batch_size, n_slots, _ = card_batch.size()
        flat_cards = card_batch.view(-1, card_batch.size(-1))
        card_enc = self.card_encoder(flat_cards)
        flat_pos = pos_indices.view(-1)
        pos_enc = self.pos_emb(flat_pos)
        combined = torch.cat([card_enc, pos_enc], dim=1)
        combined = combined.view(batch_size, n_slots, -1)
        summary = torch.sum(combined, dim=1)
        return summary, combined
    
class ShopEncoder(nn.Module):
    def __init__(self, card_encoder):
        super(ShopEncoder, self).__init__()
        self.card_encoder = card_encoder
    
    def forward(self, shop_cards):
        batch_size, shop_size, _ = shop_cards.size()
        flat_shop = shop_cards.view(batch_size, shop_size, -1)
        shop_embs = self.card_encoder(flat_shop)
        shop_embs = shop_embs.view(batch_size, shop_size, -1)
        summary = torch.sum(shop_embs, dim=1)
        return summary, shop_embs
    
class DataEncoder(nn.Module):
    def __init__(self, n_stats, hidden_size, latent_size):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(n_stats, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, latent_size)
        )
    
    def forward(self, stats):
        return self.layers(stats)

def get_emb_dim(num_cats):
    # Base formula
    dim = int(num_cats**0.5) + 1
    
    # Round up to the nearest multiple of 4 for hardware efficiency
    return (dim + 3) // 4 * 4

class Experience(NamedTuple):
    state: GameState
    action: int
    reward: float
    done: bool
    log_prob: float
    value: float
    next_value: float
    hidden: tuple

class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.episodes = []
        
    def push_episode(self, episode: list[Experience]):
        self.episodes.append(episode)
        if len(self.episodes) > self.capacity:
            self.episodes.pop(0)
    
    def sample_batch(self, batch_size, seq_len):
        batch = []
        for _ in range(batch_size):
            episode = random.choice(self.episodes)
            if len(episode) < seq_len:
                batch.append(episode)
            else:
                start = random.randint(0, len(episode) - seq_len)
                batch.append(episode[start:start+seq_len])
        return batch
    
def collate_batch(batch: list[list[Experience]], device: torch.device, seq_len: int=16):
    batch_size = len(batch)
    
    h_0 = torch.cat([ep[0].hidden[0] for ep in batch], dim=1).to(device)
    c_0 = torch.cat([ep[0].hidden[1] for ep in batch], dim=1).to(device)
    
    collated_state = {key: torch.zeros((batch_size, seq_len, *np.shape(batch[0][0].state[key])), device=device)
                      for key in batch[0][0].state.keys()}

    actions = torch.zeros((batch_size, seq_len), dtype=torch.int64, device=device)
    rewards = torch.zeros((batch_size, seq_len), dtype=torch.float32, device=device)
    dones = torch.zeros((batch_size, seq_len), device=device)
    log_probs = torch.zeros((batch_size, seq_len), dtype=torch.float32, device=device)
    values = torch.zeros((batch_size, seq_len), dtype=torch.float32, device=device)
    next_values = torch.zeros((batch_size, seq_len), dtype=torch.float32, device=device)
    mask = torch.zeros((batch_size, seq_len), device=device)
    
    for i, episode in enumerate(batch):
        for t, exp in enumerate(episode):
            if t >= seq_len:
                break
            
            for key in exp.state:
                collated_state[key][i, t] = torch.from_numpy(exp.state[key]).to(device)
            
            actions[i, t] = exp.action
            rewards[i, t] = exp.reward
            dones[i, t] = exp.done
            log_probs[i, t] = exp.log_prob
            values[i, t] = exp.value
            next_values[i, t] = exp.next_value
            mask[i, t] = 1.0

    return collated_state, actions, rewards, dones, log_probs, values, next_values, (h_0, c_0), mask

class PPOTrainer:
    def __init__(self, model: ActorCritic, replay_buffer: ReplayBuffer, optimizer, clip_param, epochs, batch_size, value_loss_coef, entropy_coef):
        self.model = model
        self.replay_buffer = replay_buffer
        self.optimizer = optimizer
        self.clip_param = clip_param
        self.epochs = epochs
        self.batch_size = batch_size
        self.value_loss_coef = value_loss_coef
        self.entropy_coef = entropy_coef
        
    def train(self, batch_size, seq_len):
        batch = self.replay_buffer.sample_batch(batch_size, seq_len)
        if batch:
            self.train_step(batch)
        
    def train_step(self, batch):
        states, actions, rewards, dones, old_log_probs, old_values, old_next_values, hidden, mask = batch
        
        returns, advantages = self.compute_advantages(rewards, dones, old_values, old_next_values, mask)
        
        for _ in range(self.epochs):
            logits, values = self.model(
                states["board_cards"],
                states["board_pos"],
                states["shop_cards"],
                states["game_data"],
                hidden
            )
            
            dist = torch.distributions.Categorical(logits=logits)
            new_log_probs = dist.log_prob(actions)
            entropy = dist.entropy()
            
            ratio = torch.exp(new_log_probs - old_log_probs)
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.clip_param, 1 + self.clip_param) * advantages
            
            action_loss = -(torch.min(surr1, surr2) * mask).sum() / mask.sum()
            value_loss = ((returns - values).pow(2) * mask).sum() / mask.sum()
            entropy_loss = (entropy * mask).sum() / mask.sum()
            loss = action_loss + self.value_loss_coef * value_loss - self.entropy_coef * entropy_loss
            
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.model.parameters(), 0.5)
            self.optimizer.step()

    def compute_advantages(self, rewards, dones, values, next_values, mask, gamma=0.99, lam=0.95):
        batch_size, T = rewards.shape()
        advantages = torch.zeros_like(rewards)
        gae = 0
            
        for t in reversed(range(T)):
            done_mask = 1.0 - dones[:, t]
            
            delta = rewards[:, t] + (gamma * next_values[:, t] * done_mask) - values[:, t]
            
            gae = delta + gamma * lam * done_mask * gae
            advantages[:, t] = gae
        returns = advantages + values
        
        valid_advantages = advantages * mask
        adv_mean = valid_advantages.mean()
        adv_std = valid_advantages.std()
        
        advantages = (advantages - adv_mean) / (adv_std + 1e-8)
        return returns, advantages
