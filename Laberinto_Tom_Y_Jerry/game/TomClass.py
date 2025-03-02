import pygame
from learning.QlearningTom import QlearningTom

class TomClass(pygame.sprite.Sprite):
    def __init__(self, TOM_START, BLOCK_SIZE, width, height, enable_render):
        # Initialize the Tom sprite
        pygame.sprite.Sprite.__init__(self)
        posX = TOM_START[0] * BLOCK_SIZE
        posY = TOM_START[1] * BLOCK_SIZE
        self.image = pygame.image.load('images/gato.png').convert()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.state = self.get_state(BLOCK_SIZE, width)
        self.qlearning = QlearningTom(width, height)

    def get_state(self, BLOCK_SIZE, width):
        # Convert the sprite's position to an index for the Q-table
        return (self.rect.y // BLOCK_SIZE) * width + (self.rect.x // BLOCK_SIZE)

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