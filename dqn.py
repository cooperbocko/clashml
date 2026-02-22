import random
from collections import deque
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

class DQN(nn.Module):
    def __init__(self, state_size: int, hidden_size: int, action_size: int):
        super().__init__()
        self.linear1 = nn.Linear(state_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, action_size)
        
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        return self.linear3(x)
    
    def save(self, file_path: str, file_name: str):
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        file_name = os.path.join(file_path, file_name)
        torch.save(self.state_dict(), file_name)
        
    def load(self, path: str):
        state_dict = torch.load(path)
        self.load_state_dict(state_dict)
        
class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
        
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = map(np.array, zip(*batch))
        return states, actions, rewards, next_states, dones
    
    def size(self):
        return len(self.buffer)
    
class QTrainer:
    def __init__(self, policy_net, target_net, replay_buffer, lr, gamma):
        self.policy_net = policy_net
        self.optimizer = optim.Adam(policy_net.parameters(), lr=lr)
        self.target_net = target_net
        self.replay_buffer = replay_buffer
        self.lr = lr
        self.gamma = gamma
        
    def train_step(self, batch_size):
        if self.replay_buffer.size() < batch_size:
            return
        
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(batch_size)
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)
        
        q_values = self.policy_net(states)
        q_value = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        
        with torch.no_grad():
            next_q_values = self.target_net(next_states)
            max_next_q = next_q_values.max(1)[0]
            target = rewards + self.gamma * max_next_q * (1 - dones)
            
        loss = F.mse_loss(q_value, target)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        tau = 0.005
        for target_param, policy_param in zip(self.target_net.parameters(), self.policy_net.parameters()):
            target_param.data.copy_(tau * policy_param.data + (1.0 - tau) * target_param.data)