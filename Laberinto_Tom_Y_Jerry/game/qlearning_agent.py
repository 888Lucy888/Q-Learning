import numpy as np
import json
import os

class QLearningAgent:
    def __init__(self, state_dim, num_actions, config_file, jerryconfig_file):
        # Initialize the Q-learning agent
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        with open(jerryconfig_file, 'r') as f:
            jerryconfig = json.load(f)
        
        self.state_dim = state_dim
        self.num_actions = num_actions
        self.alpha = config['alpha']
        self.gamma = config['gamma']
        self.epsilon = config['max_epsilon']
        self.epsilon_min = config['min_epsilon']
        self.epsilon_decay = config['decay_rate']
        self.q_table = np.zeros((state_dim, num_actions))
        self.checkpoint_dir = 'Checkpoint'
        self.checkpoint_file = os.path.join(self.checkpoint_dir, 'q_table.npy')

        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

        if jerryconfig['load_weights'] and os.path.exists(self.checkpoint_file):
            self.q_table = np.load(self.checkpoint_file)

    def choose_action(self, state_index):
        # Choose an action based on epsilon-greedy policy
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.num_actions)
        else:
            return np.argmax(self.q_table[state_index])

    def update_q_value(self, state_index, action, reward, next_state_index):
        # Update the Q-value using the Bellman equation
        best_next_action = np.argmax(self.q_table[next_state_index])
        td_target = reward + self.gamma * self.q_table[next_state_index][best_next_action]
        td_error = td_target - self.q_table[state_index][action]
        self.q_table[state_index][action] += self.alpha * td_error

    def decay_epsilon(self):
        # Decay the exploration factor over episodes
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_q_table(self):
        # Save the Q-table to a file
        np.save(self.checkpoint_file, self.q_table)