import pygame
import numpy as np
import json
import random
import os
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, output_dim)
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.relu(self.fc3(x))
        return self.fc4(x)  # Output Q-values

class QlearningTom:
    def __init__(self, width, height, config_file='config/tomqlearning.json'):
        self.width = width
        self.height = height
        self.state_size = 4  # (Cat X, Cat Y, Mouse X, Mouse Y)
        self.action_size = 4  # (Up, Down, Left, Right)
        
        # Load configuration from JSON
        with open(config_file, 'r') as file:
            config = json.load(file)

        self.gamma = config['gamma']
        self.alpha = config['alpha']
        self.epsilon = config['max_epsilon']
        self.epsilon_min = config['min_epsilon']
        self.epsilon_decay = config['decay_rate']
        self.batch_size = config['batch_size']
        self.memory_size = config['memory_size']
        self.tau = config.get('target_update_tau', 0.01)  # Soft target update factor

        # Initialize replay buffer
        self.memory = deque(maxlen=self.memory_size)

        # Initialize Neural Networks
        self.model = DQN(self.state_size, self.action_size)
        self.target_model = DQN(self.state_size, self.action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.alpha)
        self.loss_function = nn.MSELoss()

        # Load pre-trained model if exists
        if os.path.exists('dqn_gato.pth'):
            self.model.load_state_dict(torch.load('dqn_gato.pth'))
            self.target_model.load_state_dict(self.model.state_dict())
            print("Pre-trained model loaded.")

    def take_action(self, state):
        """ Choose an action using epsilon-greedy policy """
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)  # Explore
        else:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                q_values = self.model(state_tensor)
                return torch.argmax(q_values).item()  # Exploit

    def update_q_table(self, state, action, reward, next_state, done):
        """ Store experience in memory and train model """
        self.memory.append((state, action, reward, next_state, done))
        self.replay()  # Train model using replay buffer
        self.update_target_model()  # Soft update target model

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        # Sample a minibatch
        minibatch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*minibatch)

        # Convert lists to tensors
        states = torch.FloatTensor(np.array(states))
        next_states = torch.FloatTensor(np.array(next_states))
        actions = torch.LongTensor(np.array(actions)).reshape(-1, 1)
        rewards = torch.FloatTensor(np.array(rewards)).reshape(-1, 1)
        dones = torch.FloatTensor(np.array(dones)).reshape(-1, 1)

        # Compute Q-values for current states
        q_values = self.model(states).gather(1, actions)

        # Compute target Q-values using Double DQN
        next_q_values = self.target_model(next_states).max(1, keepdim=True)[0]
        expected_q_values = rewards + self.gamma * next_q_values * (1 - dones)

        # Compute loss and optimize
        loss = self.loss_function(q_values, expected_q_values.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_model(self):
        """ Soft update target model using Polyak averaging """
        for target_param, param in zip(self.target_model.parameters(), self.model.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

    def decay_epsilon(self):
        """ Decay exploration rate """
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self):
        """ Save trained model to file """
        torch.save(self.model.state_dict(), 'dqn_gato.pth')
        print("Model saved.")

    def compute_reward(self, cat_pos, mouse_pos, prev_distance):
        """ Reward shaping function """
        distance = np.linalg.norm(np.array(cat_pos) - np.array(mouse_pos))

        # Reward for getting closer to the mouse
        if distance < prev_distance:
            return 1.0  # Positive reward for moving closer
        elif distance > prev_distance:
            return -1.0  # Negative reward for moving away
        else:
            return -0.1  # Small penalty for no movement

        # Huge reward for catching the mouse
        if distance == 0:
            return 10.0

        return -0.1  # Small penalty for taking too long
