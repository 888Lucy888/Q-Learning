import pygame
import sys
import numpy as np
import time
import json
from pygame.locals import *
from game import mapaJerry
from learning.QlearningJerry import QlearningJerry

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
visor = pygame.display.set_mode((height * BLOCK_SIZE, width * BLOCK_SIZE)) if enable_render else None
pygame.display.set_caption('Q-learning Tom y Jerry')

# Cargar el mapa
nivel = mapaJerry.Mapa('game/mapaJerry.txt', enable_render)


# Posiciones iniciales
TOM_START = (1, 1)
JERRY_POS = (7, 7)  # Jerry permanece estático en la esquina opuesta

# Inicializar Q-learning
qlearning = QlearningJerry(width, height)

# Si `load_weights=True`, cargar la tabla Q preentrenada
if load_weights:
    qlearning.q_table = np.load('Checkpoint/Q_table_jerry.npy')
    qlearning.max_epsilon = qlearning.min_epsilon

class Tom(pygame.sprite.Sprite):
    def __init__(self, posX, posY, enable_render):
        pygame.sprite.Sprite.__init__(self)
        if enable_render:
            self.image = pygame.image.load('images/raton1.png').convert()
            self.image.set_colorkey((255, 255, 255))
        else:
            self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))  # Crear un bloque vacío cuando no hay render
            self.image.fill((0, 0, 255))  # Color azul para identificar a Tom en depuración
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.state = self.get_state()


    def get_state(self):
        """ Convierte la posición del sprite en un índice para la Q-table """
        return (self.rect.y // BLOCK_SIZE) * width + (self.rect.x // BLOCK_SIZE)

    def load_window(self):
        #systick
        self.clock.tick(fps)
        
        #window title
        self.draw.windowtitle(self.episode,self.steps)
        
        #close window game
        self.run = self.draw.Isquit()
        
        #refresh draw
        self.draw.window()

    def move(self, action):
        """ Mueve a Jerry según la acción proporcionada por Q-learning """
        x_before, y_before = self.rect.topleft

        if action == 'left' and self.rect.x > 0:
            self.rect.x -= BLOCK_SIZE
        elif action == 'right' and self.rect.x < (width - 1) * BLOCK_SIZE:
            self.rect.x += BLOCK_SIZE
        elif action == 'up' and self.rect.y > 0:
            self.rect.y -= BLOCK_SIZE
        elif action == 'down' and self.rect.y < (height - 1) * BLOCK_SIZE:
            self.rect.y += BLOCK_SIZE

        # Detectar colisión con paredes y revertir si es necesario
        if pygame.sprite.spritecollide(self, nivel.grupo, False):
            self.rect.x, self.rect.y = x_before, y_before  # Revertir el movimiento
            return -5  # Penalización por chocar con pared

        return -1  # Penalización pequeña por cada paso

# Instancias de los personajes
tom = Tom(TOM_START[0] * BLOCK_SIZE, TOM_START[1] * BLOCK_SIZE, enable_render)

jerry = pygame.sprite.Sprite()
if enable_render:
    jerry.image = pygame.image.load('images/q.png').convert()
    jerry.image.set_colorkey((255, 255, 255))
else:
    jerry.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))  # Bloque vacío si no hay render
    jerry.image.fill((255, 0, 0))  # Color rojo para identificar a Jerry en depuración

jerry.rect = jerry.image.get_rect()
jerry.rect.topleft = (JERRY_POS[0] * BLOCK_SIZE, JERRY_POS[1] * BLOCK_SIZE)


# Grupo de sprites
grupo_tom = pygame.sprite.RenderUpdates(tom)
grupo_jerry = pygame.sprite.RenderUpdates(jerry)

# Reloj para FPS si `enable_render=True`
clock = pygame.time.Clock() if enable_render else None

# Bucle de entrenamiento
for episode in range(max_episodes):

    for evento in pygame.event.get():
        if evento.type == QUIT or (evento.type == KEYDOWN and evento.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    tom.rect.topleft = (TOM_START[0] * BLOCK_SIZE, TOM_START[1] * BLOCK_SIZE)
    steps = 0
    run = True

    while run and steps < max_steps:
        if enable_render:
            clock.tick(fps)  # Control de FPS
            visor.fill((255, 255, 255))  # Limpiar pantalla
            nivel.actualizar(visor)
            grupo_tom.draw(visor)
            grupo_jerry.draw(visor)
            pygame.display.update()
        # Reducir exploración con el tiempo
        epsilon = qlearning.decay_epsilon(episode)
        action = qlearning.take_action(tom.get_state(), epsilon)  # Elegir acción
        reward = tom.move(action)  # Mover a Tom
        next_state = tom.get_state()

        # Si Tom encuentra a Jerry, dar recompensa y terminar episodio
        if tom.rect.topleft == jerry.rect.topleft:
            reward = 10
            run = False
            print(f"Episodio {episode+1}: ¡Tom encontró a Jerry en {steps} pasos! Epsilon = {epsilon}")

        qlearning.update_q_table(tom.state, action, reward, next_state)
        tom.state = next_state
        steps += 1

    

# Guardar la Q-table entrenada
np.save('Checkpoint/Q_table_jerry.npy', qlearning.q_table)
pygame.quit()
