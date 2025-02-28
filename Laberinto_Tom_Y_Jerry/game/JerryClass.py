import pygame
from pygame.locals import *


class JerryClass(pygame.sprite.Sprite):
    def __init__(self,JERRY_START, BLOCK_SIZE, width, enable_render):
        pygame.sprite.Sprite.__init__(self)
        posX = JERRY_START[0] * BLOCK_SIZE
        posY = JERRY_START[1] * BLOCK_SIZE
        #if enable_render:
        self.image = pygame.image.load('images/raton1.png').convert()
        self.image.set_colorkey((255, 255, 255))
        #else:
        #    self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))  # Crear un bloque vacío cuando no hay render
        #    self.image.fill((0, 0, 255))  # Color azul para identificar a Jerry en depuración
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.state = self.get_state(BLOCK_SIZE, width)


    def get_state(self, BLOCK_SIZE, width):
        """ Convierte la posición del sprite en un índice para la Q-table """
        return (self.rect.y // BLOCK_SIZE) * width + (self.rect.x // BLOCK_SIZE)

    def load_window(self, fps):
        #systick
        self.clock.tick(fps)
        
        #window title
        self.draw.windowtitle(self.episode,self.steps)
        
        #close window game
        self.run = self.draw.Isquit()
        
        #refresh draw
        self.draw.window()

    def move(self, action, nivel, BLOCK_SIZE, width, height):
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
            return -50  # Penalización por chocar con pared

        return 10  # Penalización pequeña por cada paso opcional