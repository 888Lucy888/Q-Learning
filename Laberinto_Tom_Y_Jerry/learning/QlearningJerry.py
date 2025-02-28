import random
import numpy as np
import json

# Cargar parámetros de Q-learning desde JSON
file_name = 'config/jerryqlearning.json'
with open(file_name, 'r') as file:
    data = json.load(file)

# Parámetros de Q-learning
max_epsilon = data['max_epsilon']
min_epsilon = data['min_epsilon']
decay_rate = data['decay_rate']
alpha = data['alpha']
gamma = data['gamma']

actions = ['up', 'down', 'left', 'right']

class QlearningJerry:
    def __init__(self, width, height, total_quesos):
        self.width = width
        self.height = height
        self.q_table = np.zeros((total_quesos, width * height, 4))

    def take_action(self,state, epsilon, queso_actual):
        if random.random() > epsilon:
            return actions[np.argmax(self.q_table[queso_actual][state])]
        else:
            possible_actions = []
            if state < self.height*(self.height-1):
                possible_actions.append('down')
            if state >= self.height:
                possible_actions.append('up')
            if state % self.width != 0:
                possible_actions.append('left')
            if state % self.width != self.width-1:
                possible_actions.append('right')
            return random.choice(possible_actions)

    def update_q_table(self, state, action, reward, next_state, queso_actual):
        """ Actualiza la Q-table con la ecuación de Bellman """
        self.q_table[queso_actual][state][actions.index(action)] += alpha * (
            reward + gamma * np.max(self.q_table[queso_actual][next_state]) - self.q_table[queso_actual][state][actions.index(action)]
        )

    def decay_epsilon(self, episode, load_weights):
        """ Reduce el factor de exploración a lo largo de los episodios """
        if load_weights:
            self.epsilon = min_epsilon + (min_epsilon - min_epsilon) * np.exp(-decay_rate * episode)
        else:
            self.epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay_rate * episode)
        return self.epsilon
