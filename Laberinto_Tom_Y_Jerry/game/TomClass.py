import pygame
from learning.QlearningTom import QlearningTom
import numpy as np
class TomClass(pygame.sprite.Sprite):
    def __init__(self, TOM_START, BLOCK_SIZE, width, height, enable_render, jerry):
        # Initialize the Tom sprite
        pygame.sprite.Sprite.__init__(self)
        posX = TOM_START[0] * BLOCK_SIZE
        posY = TOM_START[1] * BLOCK_SIZE
        self.image = pygame.image.load('images/gato.png').convert()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.state = self.get_state(BLOCK_SIZE, width,height, jerry)
        self.qlearning = QlearningTom(width, height)

    def get_state(self, BLOCK_SIZE, width, height, jerry):
        tom_x, tom_y = self.rect.topleft
        jerry_x, jerry_y = jerry.rect.topleft  # Get Jerry's position
      
        # Normalize positions by dividing by grid size
        return np.array([
            tom_x / (width * BLOCK_SIZE),
            tom_y / (height * BLOCK_SIZE),
            jerry_x / (width * BLOCK_SIZE),
            jerry_y / (height * BLOCK_SIZE)
        ], dtype=np.float32)


    def move(self, action, nivel, BLOCK_SIZE, width, height):
        # Move Tom according to the action provided
        x_before, y_before = self.rect.topleft

        if action == 0 and self.rect.x > 0:  # left
            self.rect.x -= BLOCK_SIZE
        elif action == 1 and self.rect.x < (width - 1) * BLOCK_SIZE:  # right
            self.rect.x += BLOCK_SIZE
        elif action == 2 and self.rect.y > 0:  # up
            self.rect.y -= BLOCK_SIZE
        elif action == 3 and self.rect.y < (height - 1) * BLOCK_SIZE:  # down
            self.rect.y += BLOCK_SIZE

        # Detect collision with walls and revert if necessary
        if pygame.sprite.spritecollide(self, nivel.grupo, False):
            self.rect.x, self.rect.y = x_before, y_before  # Revert the movement
            return -50  # Penalty for hitting a wall

        return 10  # Small penalty for each step