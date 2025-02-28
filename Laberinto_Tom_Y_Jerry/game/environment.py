import numpy as np
import pygame
from game import mapa

class MazeEnvironment:
    def __init__(self, maze_file):
        self.maze = mapa.Mapa(maze_file)
        self.agent_position = (1, 1)  # Starting position of the agent
        self.initial_cheeses = [(1, 5), (1, 10), (3, 3), (5, 5), (7, 7)]  # Example positions
        self.cheeses = self.initial_cheeses.copy()
        self.grid_width = 20
        self.grid_height = 15
        self.size = self.grid_width * self.grid_height  # Assuming a 20x15 grid

    def reset(self):
        self.agent_position = (1, 1)
        self.cheeses = self.initial_cheeses.copy()
        return self.get_state()

    def get_state(self):
        # Combine agent position and cheeses positions into a single state representation
        return (self.agent_position, tuple(self.cheeses))

    def get_state_index(self, state):
        # Convert the state representation to a single integer index
        agent_pos, cheeses = state
        # Flatten the state to a single index
        return agent_pos[0] * self.grid_width + agent_pos[1]

    def step(self, action):
        x, y = self.agent_position
        if action == 0:  # Up
            y -= 1
        elif action == 1:  # Down
            y += 1
        elif action == 2:  # Left
            x -= 1
        elif action == 3:  # Right
            x += 1

        new_position = (x, y)
        if self.is_valid_position(new_position):
            self.agent_position = new_position

        reward = -1  # Default step cost
        done = False

        if new_position in self.cheeses:
            self.cheeses.remove(new_position)
            reward = 10  # Reward for collecting cheese
            if not self.cheeses:
                done = True  # All cheeses collected

        return self.get_state(), reward, done

    def is_valid_position(self, position):
        x, y = position
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return False
        
        # Create a temporary sprite for collision detection
        temp_sprite = pygame.sprite.Sprite()
        temp_sprite.rect = pygame.Rect(x * 40, y * 40, 40, 40)
        
        return not pygame.sprite.spritecollideany(temp_sprite, self.maze.grupo)
