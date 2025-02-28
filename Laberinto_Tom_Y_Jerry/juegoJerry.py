import pygame
import sys
import numpy as np
import time
import json
from pygame.locals import *
from game import mapaJerry
from learning.QlearningJerry import QlearningJerry
from game.JerryClass import JerryClass

# Cargar configuración desde JSON
file_name = 'config/jerryconfig.json'
with open(file_name, 'r') as file:
    data = json.load(file)

# Parámetros desde el JSON
fps = data['fps']
max_steps = data['max_steps']
max_episodes = data['max_episodes']
width = data['width']
height = data['height']
load_weights = data['load_weights']
enable_render = data['enable_render']

pygame.init()

# Parámetros de pantalla
BLOCK_SIZE = 40  
visor = pygame.display.set_mode((width * BLOCK_SIZE, height * BLOCK_SIZE))
pygame.display.set_caption('Q-learning Jerry')

# Cargar el mapa
nivel = mapaJerry.Mapa('game/mapaJerry.txt', enable_render)

# Se guarda la cantidad de quesos existentes en total_quesos para obtener el número de quesos comido
total_quesos = len(nivel.quesos)


# Posiciones iniciales
JERRY_START = (1, 6)

# Inicializar Q-learning
qlearning = QlearningJerry(width, height, total_quesos)

# Inicializa a Jerry
jerry = JerryClass(JERRY_START, BLOCK_SIZE, width, enable_render)

# Si `load_weights=True`, cargar la tabla Q preentrenada
if load_weights:
    qlearning.q_table = np.load('Checkpoint/Q_table_jerry.npy')
    

# Grupo de sprites
grupo_jerry = pygame.sprite.RenderUpdates(jerry)

# Reloj para FPS si `enable_render=True`
clock = pygame.time.Clock() if enable_render else None

# Bucle de entrenamiento
for episode in range(max_episodes):
    # Se vuelve a cargar el mapa para el siguiente episodio
    nivel = mapaJerry.Mapa('game/mapaJerry.txt', enable_render)
    # Se guarda la cantidad de quesos existentes en num_quesos para definir la recompensa y terminar los episodios
    num_quesos = total_quesos

    for evento in pygame.event.get():
        if evento.type == QUIT or (evento.type == KEYDOWN and evento.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    jerry.rect.topleft = (JERRY_START[0] * BLOCK_SIZE, JERRY_START[1] * BLOCK_SIZE)
    steps = 0
    run = True

    while run and steps < max_steps:
        if enable_render:
            clock.tick(fps)  # Control de FPS
            visor.fill((255, 255, 255))  # Limpiar pantalla
            nivel.actualizar(visor)
            grupo_jerry.draw(visor)
            pygame.display.update()
        
        # Número de queso que se está tratando de comer
        queso_actual = total_quesos - num_quesos
        # Reducir exploración con el tiempo
        epsilon = qlearning.decay_epsilon(episode, load_weights)
        action = qlearning.take_action(jerry.get_state(BLOCK_SIZE, width), epsilon, queso_actual)  # Elegir acción
        reward = jerry.move(action, nivel, BLOCK_SIZE, width, height)  # Mover a jerry
        next_state = jerry.get_state(BLOCK_SIZE, width)

        for pum in pygame.sprite.groupcollide(grupo_jerry, nivel.quesos, 0, 1):
            pass

        # Si Jerry encuentra al queso, dar recompensa
        if len(nivel.quesos) < num_quesos:
            reward = 100
            num_quesos = len(nivel.quesos)
            #print(f"Epsilon = {epsilon}")
            
            if len(nivel.quesos) == 0:
                run = False
                print(f"Episodio {episode+1}: ¡Jerry encontró los {total_quesos} quesos en {steps} pasos!, Epsilon = {epsilon}")
        else:
            reward -= 50

        qlearning.update_q_table(jerry.state, action, reward, next_state, queso_actual)
        jerry.state = next_state
        steps += 1

    

# Guardar la Q-table entrenada

np.save('Checkpoint/Q_table_jerry.npy', qlearning.q_table)
pygame.quit()
