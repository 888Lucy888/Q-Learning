# -*- coding: utf-8 -*-
import pygame, sys
from pygame.locals import *
from game import mapa
from game.environment import MazeEnvironment
from game.qlearning_agent import QLearningAgent
import time
import json

pygame.mixer.pre_init(44100,16,2,1024)
pygame.init()

BLANCO = (255,255,255)
AMARILLO = (255,255,0)

tipoLetra = pygame.font.Font('Grandezza.ttf', 30)
tipoLetra2 = pygame.font.Font('Grandezza.ttf', 35)

imagenDeFondo = 'images/Noticia_TomJerry.jpg'
imagenGatoContento = 'images/gato.png'
imagenRatonContento = 'images/raton1.png'
imagenQueso = 'images/q.png'

visor = pygame.display.set_mode((800, 600))

def pausa():
   # Esta función hace que se espera hasta que se pulse una tecla
   esperar = True
   while esperar:
      for evento in pygame.event.get():
          if evento.type == KEYDOWN:
              esperar = False

def mostrarIntro():
   # Muestra la pantalla de inicio y espera
   fondo = pygame.image.load(imagenDeFondo).convert()
   visor.blit(fondo, (0,0))
   mensaje = 'Pulsa una tecla para comenzar'
   texto = tipoLetra.render(mensaje, True, AMARILLO)
  
   visor.blit(texto, (60,550,350,30))
   pygame.display.update()
   pausa()

# Load configuration
with open('config/jerryconfig.json', 'r') as f:
    config = json.load(f)

pygame.mouse.set_visible(False)

if config['enable_render']:
    mostrarIntro()

time.sleep(0.75)

class imagenRatonContento( pygame.sprite.Sprite ):
    def __init__( self, posX, posY ):
        pygame.sprite.Sprite.__init__( self )
        self.image = pygame.image.load('images/raton1.png').convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.dy = 0
        self.dx = 0
                
    def update(self):
        self.pos = self.rect.topleft
        self.rect.move_ip(self.dx,self.dy)
        
    def deshacer(self):
        self.rect.topleft = self.pos

class imagenGatoContento( pygame.sprite.Sprite ):
    def __init__( self, posX, posY ):
        pygame.sprite.Sprite.__init__( self )
        self.image = pygame.image.load('images/gato.png').convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.dy = 0
        self.dx = 0
                
    def update(self):
        self.pos = self.rect.topleft
        self.rect.move_ip(self.dx,self.dy)
        
    def deshacer(self):
        self.rect.topleft = self.pos

visor = pygame.display.set_mode((800, 600), 0, 32)
pygame.display.set_caption('Ejemplo de Mapa')

imagenRatonContento = imagenRatonContento(50,200)
imagenGatoContento = imagenGatoContento(50,500)

grupoimagenRatonContento = pygame.sprite.RenderUpdates( imagenRatonContento )
grupoimagenGatoContento = pygame.sprite.RenderUpdates( imagenGatoContento )

nivel = mapa.Mapa('game/mapa.txt')

reloj = pygame.time.Clock()

# Q-Learning setup
env = MazeEnvironment('game/mapa.txt')
state_dim = env.size  # Use the size of the environment
agent = QLearningAgent(state_dim=state_dim, num_actions=4, config_file='config/jerryqlearning.json', jerryconfig_file='config/jerryconfig.json')

max_episodes = config['max_episodes']

for episode in range(max_episodes):
    state = env.reset()
    done = False
    while not done:
        state_index = env.get_state_index(state)
        action = agent.choose_action(state_index)
        next_state, reward, done = env.step(action)
        next_state_index = env.get_state_index(next_state)
        agent.update_q_value(state_index, action, reward, next_state_index)
        state = next_state
    agent.decay_epsilon()
    agent.save_q_table()

while True:
    reloj.tick(config['fps'])
    
    for evento in pygame.event.get():
        if evento.type == QUIT or (evento.type == KEYDOWN and evento.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
    
    if imagenGatoContento.rect.right > 800:
        pygame.quit()
        sys.exit()
    
    teclasPulsadas = pygame.key.get_pressed()
    
    if teclasPulsadas[K_a]:
        imagenGatoContento.dx = -2
    elif teclasPulsadas[K_d]:
        imagenGatoContento.dx = 2
    else:
        imagenGatoContento.dx = 0
        
    if teclasPulsadas[K_w]:
        imagenGatoContento.dy = -2
    elif teclasPulsadas[K_x]:
        imagenGatoContento.dy = 2
    else:
        imagenGatoContento.dy = 0
    
    if imagenRatonContento.rect.right > 800:
        pygame.quit()
        sys.exit()
    
    teclasPulsadas = pygame.key.get_pressed()
    
    if teclasPulsadas[K_LEFT]:
        imagenRatonContento.dx = -2
    elif teclasPulsadas[K_RIGHT]:
        imagenRatonContento.dx = 2
    else:
        imagenRatonContento.dx = 0
        
    if teclasPulsadas[K_UP]:
        imagenRatonContento.dy = -2
    elif teclasPulsadas[K_DOWN]:
        imagenRatonContento.dy = 2
    else:
        imagenRatonContento.dy = 0
    
    grupoimagenRatonContento.update()
    grupoimagenGatoContento.update()
  
    if pygame.sprite.spritecollide(imagenRatonContento, nivel.grupo, 0, pygame.sprite.collide_mask):
        imagenRatonContento.deshacer()
        
    if pygame.sprite.spritecollide(imagenGatoContento, nivel.grupo, 0, pygame.sprite.collide_mask):
        imagenGatoContento.deshacer()
    
    for pum in pygame.sprite.groupcollide(grupoimagenRatonContento, nivel.quesos, 0, 1):
        pass

    # Check if all cheeses are collected
    if len(nivel.quesos) == 0:
        pygame.quit()
        sys.exit()
  
    # Check if gato.png touches raton1.png
    if pygame.sprite.spritecollide(imagenRatonContento, grupoimagenGatoContento, 0, pygame.sprite.collide_mask):
        pygame.quit()
        sys.exit()

    nivel.actualizar(visor)
    grupoimagenRatonContento.draw(visor)
    grupoimagenGatoContento.draw(visor)
    pygame.display.update()
