import pygame
import numpy as np
import json
import random
import time
import os
import math
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)  # Q-values for all actions


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

    def update_q_table(self, state, action, reward, next_state):
        """ Store experience in memory and train model """
        self.memory.append((state, action, reward, next_state))
        self.replay()  # Train model using replay buffer

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        # Sample a minibatch
        minibatch = random.sample(self.memory, self.batch_size)

        # Convert minibatch into NumPy arrays
        states, actions, rewards, next_states = zip(*minibatch)

        # Convert lists of NumPy arrays into single NumPy arrays
        states = np.array(states, dtype=np.float32)  # Shape: (batch_size, state_size)
        next_states = np.array(next_states, dtype=np.float32)  # Shape: (batch_size, state_size)
        actions = np.array(actions, dtype=np.int64).reshape(-1, 1)  # Shape: (batch_size, 1)
        rewards = np.array(rewards, dtype=np.float32).reshape(-1, 1)  # Shape: (batch_size, 1)

        # Convert to PyTorch tensors
        states = torch.FloatTensor(states)  # Shape: (batch_size, state_size)
        next_states = torch.FloatTensor(next_states)  # Shape: (batch_size, state_size)
        actions = torch.LongTensor(actions)  # Shape: (batch_size, 1)
        rewards = torch.FloatTensor(rewards)  # Shape: (batch_size, 1)

        
        # Compute Q-values for current states
        q_values = self.model(states)  # Shape: (batch_size, action_size)

        # Gather the Q-values corresponding to the actions taken
        
        q_values = q_values.squeeze(1).gather(1, actions)  # Fix shape mismatch

        # Compute target Q-values
        next_q_values = self.target_model(next_states).max(1, keepdim=True)[0]  # Shape: (batch_size, 1)
        expected_q_values = rewards + self.gamma * next_q_values  # Shape: (batch_size, 1)

        # Compute loss and optimize
        loss = self.loss_function(q_values, expected_q_values.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def decay_epsilon(self):
        """ Decay exploration rate """
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self):
        """ Save trained model to file """
        torch.save(self.model.state_dict(), 'dqn_gato.pth')
        print("Model saved.")