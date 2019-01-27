"""Constant values that are used throughout the program."""

# Colours for UI rendering in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)

# Environment parameters
DRAW_SENSORS = True  # Whether to render sensors in environment or not.
TIME_LIMIT = 820  # Maximum time for each generation.

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200

# Training parameters
POOL_SIZE = 20  # Population size for each generation.
TARGET_TIME = 5999  # Minimum time in seconds required for training termination
TOPOLOGY = [5, 3, 2]  # Neural network structure for any of the cars.

# Genetic algorithm parameters
CROSSOVER_RATE = 0.7  # Probability of child being produced.
MUTATION_RATE = 0.05  # Probability of mutation occurring on a specified weight.
