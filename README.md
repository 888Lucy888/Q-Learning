# Tom & Jerry Labyrinth

## Team

- Constanza Corvera
- Pablo Tazaki
- Miguel Vizcaíno
- Lucia Castañeda

## Overview

"Laberinto Tom y Jerry" is a reinforcement learning project where two agents, Tom and Jerry, navigate a maze. Jerry's goal is to collect all the cheeses in the maze, while Tom's goal is to catch Jerry. The agents are trained using Q-learning, a model-free reinforcement learning algorithm.

## Tools and Libraries Used

- **Python**: The programming language used for the project.
  - Version: 3.11
- **Pygame**: A library used for creating the game environment and rendering the graphics.
  - Version: 2.1.0
- **NumPy**: A library used for numerical computations and handling the Q-tables.
  - Version: 1.23.4
- **JSON**: Used for configuration files to store parameters for the Q-learning agents.
- **Matplotlib**: A library used for plotting the results of the Q-learning training.
  - Version: 3.6.1
- **PyTorch**: A library used for implementing the Deep Q-Learning model for Tom.
  - Version: 1.12.1

## Game Description

The game consists of a maze where:

- **Jerry** starts at a predefined position and aims to collect all the cheeses scattered throughout the maze.
- **Tom** starts at a different predefined position and aims to catch Jerry.

The maze is represented as a grid, and both agents can move up, down, left, or right. The game ends when Jerry collects all the cheeses or when Tom catches Jerry.

## Q-learning Agents

### Jerry's Q-learning Agent

Jerry's agent is trained to navigate the maze and collect all the cheeses while avoiding Tom. The Q-learning algorithm is used to update the Q-table based on the rewards received from the environment.

#### Parameters

- **Alpha (α)**: Learning rate, which determines how much new information overrides the old information.
- **Gamma (γ)**: Discount factor, which determines the importance of future rewards.
- **Epsilon (ε)**: Exploration rate, which determines the probability of choosing a random action over the best-known action.

#### Rewards

- **+10000**: For collecting a cheese.
- **-10000**: For exceeding `max_steps` without collecting all cheeses.
- **-5000**: For getting captured by Tom.
- **-50**: For moving closer to Tom.
- **-50**: For hitting a wall.
- **-10**: For not collecting a cheese in the current step.
- **-1 × current step**: Time penalty until a cheese is collected.

#### Actions

- **Up**: Move up in the grid.
- **Down**: Move down in the grid.
- **Left**: Move left in the grid.
- **Right**: Move right in the grid.

### Tom's Q-learning Agent

Tom's agent is trained to navigate the maze and catch Jerry. The Q-learning algorithm is used to update the Q-table based on the rewards received from the environment.

#### Parameters

- **Alpha (α)**: Learning rate, which determines how much new information overrides the old information.
- **Gamma (γ)**: Discount factor, which determines the importance of future rewards.
- **Epsilon (ε)**: Exploration rate, which determines the probability of choosing a random action over the best-known action.

#### Rewards

- **+1000**: For catching Jerry.
- **-50**: For hitting a wall.
- **+50**: For getting closer to Jerry.

#### Actions

- **0**: Move left in the grid.
- **1**: Move right in the grid.
- **2**: Move up in the grid.
- **3**: Move down in the grid.

## Training Process

The training process involves running multiple episodes where the agents interact with the environment and update their Q-tables based on the rewards received.

### Jerry's Training Process

1. **Initialization**: Jerry starts at a predefined position, and the Q-table is initialized with zeros.
2. **Action Selection**: Jerry selects an action based on the epsilon-greedy policy.
3. **State Transition**: Jerry moves to the new state based on the selected action.
4. **Reward Calculation**: Jerry receives a reward based on the new state.
5. **Q-table Update**: The Q-table is updated using the Bellman equation.
6. **Epsilon Decay**: The exploration rate is decayed over episodes to reduce exploration over time.

### Tom's Training

1. **Initialization**: Tom starts at a predefined position, and the Q-table is initialized with zeros.
2. **Action Selection**: Tom selects an action based on the epsilon-greedy policy.
3. **State Transition**: Tom moves to the new state based on the selected action.
4. **Reward Calculation**: Tom receives a reward based on the new state.
5. **Q-table Update**: The Q-table is updated using the Bellman equation.
6. **Epsilon Decay**: The exploration rate is decayed over episodes to reduce exploration over time.

## How to Run the Game

1. **Install Dependencies**: Ensure you have Python, Pygame, NumPy, Matplotlib, and PyTorch installed. You can install the required libraries using the following commands:

   ```bash
   pip install pygame numpy matplotlib torch
   ```

2. **Run the Game**: Execute the [juegoRun.py](http://_vscodecontentref_/2) script to start the game and observe the agents' behavior.
   ```bash
   python juegoRun.py
   ```

## Configuration Files

The configuration files for the Q-learning agents are stored in the `config` directory. These files contain the parameters for the Q-learning algorithm and can be modified to change the behavior of the agents.

- **config.json**: Configuration file of the training execution parameters.
- **jerryqlearning.json**: Configuration file for Jerry's Q-learning agent.
- **tomqlearning.json**: Configuration file for Tom's Q-learning agent.

## Conclusion

This project demonstrates the application of Q-learning and Deep Q-Learning in a game environment where two agents, Tom and Jerry, interact with each other. The agents learn to navigate the maze and achieve their respective goals through reinforcement learning.

At the end of the training, a bar graph is displayed showing the number of wins for Jerry, the number of wins for Tom, and the number of episodes where the action limit was reached without a winner. This helps visualize the performance of the agents over the training episodes.

Feel free to explore the code, modify the parameters, and experiment with different configurations to see how the agents' behavior changes.
