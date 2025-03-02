import numpy as np
import json

class QlearningTom:
    def __init__(self, width, height, config_file='config/tomqlearning.json'):
        # Initialize the Q-learning agent for Tom
        self.width = width
        self.height = height
        self.q_table = np.zeros((width * height, 4))  # 4 actions: left, right, up, down
        
        # Load configuration from JSON file
        with open(config_file, 'r') as file:
            config = json.load(file)
        
        self.alpha = config['alpha']  # Learning rate
        self.gamma = config['gamma']  # Discount factor
        self.epsilon = config['max_epsilon']  # Initial exploration rate
        self.epsilon_min = config['min_epsilon']
        self.epsilon_decay = config['decay_rate']

    def take_action(self, state):
        # Choose an action based on epsilon-greedy policy
        if np.random.rand() < self.epsilon:
            return np.random.choice(4)  # Explore: random action
        return np.argmax(self.q_table[state])  # Exploit: best action

    def update_q_table(self, state, action, reward, next_state):
        # Update the Q-table using the Bellman equation
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.gamma * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.alpha * td_error

    def decay_epsilon(self):
        # Decay the exploration factor over episodes
        if self.epsilon > self.epsilon_min:
            self.epsilon -= self.epsilon_decay
            if self.epsilon < self.epsilon_min:
                self.epsilon = self.epsilon_min