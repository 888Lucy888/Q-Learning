import pygame
from pygame.locals import *

class JerryClass(pygame.sprite.Sprite):
    def __init__(self, JERRY_START, BLOCK_SIZE, width, enable_render):
        # Initialize the Jerry sprite
        pygame.sprite.Sprite.__init__(self)
        posX = JERRY_START[0] * BLOCK_SIZE
        posY = JERRY_START[1] * BLOCK_SIZE
        self.image = pygame.image.load('images/raton1.png').convert()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.state = self.get_state(BLOCK_SIZE, width)

    def get_state(self, BLOCK_SIZE, width):
        # Convert the sprite's position to an index for the Q-table
        return (self.rect.y // BLOCK_SIZE) * width + (self.rect.x // BLOCK_SIZE)

    def load_window(self, fps):
        # Load the game window with specified FPS
        self.clock.tick(fps)
        self.draw.windowtitle(self.episode, self.steps)
        self.run = self.draw.Isquit()
        self.draw.window()

    def move(self, action, nivel, BLOCK_SIZE, width, height):
        # Move Jerry according to the action provided by Q-learning
        x_before, y_before = self.rect.topleft

        if action == 'left' and self.rect.x > 0:
            self.rect.x -= BLOCK_SIZE
        elif action == 'right' and self.rect.x < (width - 1) * BLOCK_SIZE:
            self.rect.x += BLOCK_SIZE
        elif action == 'up' and self.rect.y > 0:
            self.rect.y -= BLOCK_SIZE
        elif action == 'down' and self.rect.y < (height - 1) * BLOCK_SIZE:
            self.rect.y += BLOCK_SIZE

        # Detect collision with walls and revert if necessary
        if pygame.sprite.spritecollide(self, nivel.grupo, False):
            self.rect.x, self.rect.y = x_before, y_before  # Revert the movement
            return -50  # Penalty for hitting a wall

        return 10  # Small penalty for each step