import pygame
import sys
import numpy as np
import time
import json
import matplotlib.pyplot as plt
from pygame.locals import *
from game import mapaJerry
from learning.QlearningJerry import QlearningJerry
from learning.QlearningTom import QlearningTom
from game.JerryClass import JerryClass
from game.TomClass import TomClass
import torch
import torch.nn as nn
import torch.optim as optim

# Load configuration from JSON
file_name = 'config/config.json'
with open(file_name, 'r') as file:
    data = json.load(file)

# Parameters from JSON
fps = data['fps']
max_steps = data['max_steps']
max_episodes = data['max_episodes']
width = data['width']
height = data['height']
load_weights = data['load_weights']
enable_render = data['enable_render']

pygame.init()

# Screen parameters
BLOCK_SIZE = 40  
visor = pygame.display.set_mode((width * BLOCK_SIZE, height * BLOCK_SIZE))
pygame.display.set_caption('Q-learning Jerry')

# Load the map
nivel = mapaJerry.Mapa('game/mapaJerry.txt', enable_render)

# Store the total number of cheeses
total_quesos = len(nivel.quesos)

# Initial positions
JERRY_START = (1, 6)
TOM_START = (16, 6)

# Initialize Q-learning
qlearning_jerry = QlearningJerry(width, height, total_quesos)
qlearning_tom = QlearningTom(width, height, config_file='config/tomqlearning.json')

# Initialize Jerry and Tom
jerry = JerryClass(JERRY_START, BLOCK_SIZE, width, enable_render)
tom = TomClass(TOM_START, BLOCK_SIZE, width, height, enable_render,jerry)

# If `load_weights=True`, load the pre-trained Q-table
if load_weights:
    qlearning_jerry.q_table = np.load('Checkpoint/Q_table_jerry_Run.npy')
    qlearning_tom.q_table = np.load('Checkpoint/Q_table_tom_Run.npy')

# Sprite groups
grupo_jerry = pygame.sprite.RenderUpdates(jerry)
grupo_tom = pygame.sprite.RenderUpdates(tom)

# Clock for FPS if `enable_render=True`
clock = pygame.time.Clock() if enable_render else None

def calculate_distance(pos1, pos2):
    """Calculate the Manhattan distance between two positions"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# Initialize win counters
jerry_wins = 0
tom_wins = 0
action_limit_reached = 0

# Training loop
for episode in range(max_episodes):
    # Reload the map for the next episode
    nivel = mapaJerry.Mapa('game/mapaJerry.txt', enable_render)
    # Store the number of remaining cheeses
    num_quesos = total_quesos

    for evento in pygame.event.get():
        if evento.type == QUIT or (evento.type == KEYDOWN and evento.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    jerry.rect.topleft = (JERRY_START[0] * BLOCK_SIZE, JERRY_START[1] * BLOCK_SIZE)
    tom.rect.topleft = (TOM_START[0] * BLOCK_SIZE, TOM_START[1] * BLOCK_SIZE)
    steps = 0
    chese_time_counter = 0
    run = True

    while run and steps < max_steps:
        if enable_render:
            clock.tick(fps)  # Control FPS
            visor.fill((255, 255, 255))  # Clear screen
            nivel.actualizar(visor)
            grupo_jerry.draw(visor)
            grupo_tom.draw(visor)
            pygame.display.update()
        
        # Number of cheese being targeted
        queso_actual = total_quesos - num_quesos
        # Reduce exploration over time
        epsilon_jerry = qlearning_jerry.decay_epsilon(episode, load_weights)
        epsilon_tom = qlearning_tom.decay_epsilon()
        action_jerry = qlearning_jerry.take_action(jerry.get_state(BLOCK_SIZE, width), epsilon_jerry, queso_actual)  # Choose action
        #action_tom = qlearning_tom.take_action(tom.get_state(BLOCK_SIZE, width))  # Choose action

        # Use DQN model to choose action for Tom
        tom_state = tom.get_state(BLOCK_SIZE, width, height, jerry)  # Pass Jerry's position
        tom_state = np.array(tom_state, dtype=np.float32).reshape(1, -1)  # Ensure correct shape
        action_tom = qlearning_tom.take_action(tom_state)

        # Calculate distance before movement
        distance_before = calculate_distance(jerry.rect.topleft, tom.rect.topleft)

        reward_jerry = jerry.move(action_jerry, nivel, BLOCK_SIZE, width, height)  # Move Jerry
        reward_tom = tom.move(action_tom, nivel, BLOCK_SIZE, width, height)  # Move Tom
        #reward_tom = 0

        # Calculate distance after movement
        distance_after = calculate_distance(jerry.rect.topleft, tom.rect.topleft)

        # Reward Tom and penalty Jerry if Tom gets closer to Jerry
        if distance_after < distance_before:
            reward_tom += 50
            reward_jerry -=50

        next_state_jerry = jerry.get_state(BLOCK_SIZE, width)
        next_state_tom = tom.get_state(BLOCK_SIZE, width, height,jerry)

        for pum in pygame.sprite.groupcollide(grupo_jerry, nivel.quesos, 0, 1):
            pass

        # If Jerry finds cheese, give reward
        if len(nivel.quesos) < num_quesos:
            reward_jerry = 1000
            num_quesos = len(nivel.quesos)
            chese_time_counter = 0
            
            if len(nivel.quesos) == 0:
                run = False
                jerry_wins += 1
                print(f"Episodio {episode+1}: ¡Jerry encontró los {total_quesos} quesos en {steps} pasos!, Epsilon = {epsilon_jerry}")
        else:
            reward_jerry -= 10

        # Penalty if Tom catches Jerry
        if jerry.rect.topleft == tom.rect.topleft:
            reward_jerry -= 5000  # Worst punishment for Jerry
            reward_tom += 1000  # Reward for Tom
            run = False
            tom_wins += 1
            print(f"Episodio {episode+1}: ¡Tom atrapó a Jerry en {steps} pasos!, Epsilon = {epsilon_jerry}")

        qlearning_jerry.update_q_table(jerry.state, action_jerry, reward_jerry, next_state_jerry, queso_actual)
        qlearning_tom.update_q_table(tom.state, action_tom, reward_tom, next_state_tom)
        jerry.state = next_state_jerry
        tom.state = next_state_tom
        steps += 1
        chese_time_counter += 1
        # Penalty time spent  
        reward_jerry -= chese_time_counter

    # Penalty if Jerry doesn't collect all cheeses or Tom doesn't catch Jerry
    if steps >= max_steps and len(nivel.quesos) > 0:
        reward_jerry -= 10000  # Worst punishment for Jerry
        action_limit_reached += 1
        print(f"Episodio {episode+1}: ¡Jerry no recogió todos los quesos en {steps} pasos!")

# Save the trained Q-table
np.save('Checkpoint/Q_table_jerry_Run.npy', qlearning_jerry.q_table)
torch.save(qlearning_tom.model.state_dict(), 'Checkpoint/dqn_gato.pth')  # Save DQN model
pygame.quit()

# Plot the results
labels = ['Jerry Wins', 'Tom Wins', 'Action Limit Reached']
counts = [jerry_wins, tom_wins, action_limit_reached]

plt.bar(labels, counts, color=['#add8e6', '#ffcccb', '#d3d3d3'])
plt.xlabel('Outcome')
plt.ylabel('Number of Episodes')
plt.title('Results of Q-learning Training')
plt.show()
