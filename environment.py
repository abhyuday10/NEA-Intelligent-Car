"""This module is used by the ML_controller for the training simulation and visualisation.PyGame is used for the rendering."""

import math
import random
import sys

import pygame
import thorpy as tp  # tkinter wrapper for the GUI

import constants
import car

# Initialize the Pygame library
pygame.init()


class CircleObstacle:
    """Circular obstacle class to manage an obstacle instance in the environment
    Can be instantiated with coordinates, movement velocity and radius."""

    def __init__(self, colour, x, y, move, radius):
        self.moveX = move[0]  # x velocity
        self.moveY = move[1]  # y velocity

        self.colour = colour
        self.pos = [x, y]
        self.radius = radius

    def draw_to_screen(self, screen):
        """Simple function to render this object onto the screen using Pygame"""
        pygame.draw.circle(screen, self.colour, self.pos, self.radius)


class Environment:
    """Environment class to evaluate one generation of solutions
    Takes a list of the solutions as input
    Returns the evaluated solutions and their fitness"""

    # Initialising environment variables
    clock = pygame.time.Clock()  # Pygame clock to sync FPS
    screen_size = width, height = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Intelligent Driver')

    def __init__(self, solution_list, gen):
        self.running = True

        rectx = 200
        recty = 400

        # Specifying area where obstacles do not spawn
        self.spawnrect = [(self.width / 2) - rectx / 2, (self.height / 2) + recty / 20, rectx, recty]

        # Specifying area where cars spawn
        self.carStartPos = [self.spawnrect[0] + 100, self.spawnrect[1] + 100]

        # Generate obstacles, borders and cars into environment
        self.obstacles = self.generate_obstacles()
        self.borders = self.create_borders()
        self.cars = self.generate_cars(solution_list)

        self.evaluatedCars = []  # List to put cars in once evaluated

        self.generation_number = gen
        self.time = 0

        self.pop_size = len(solution_list)
        self.set_borders()

        # Begin evaluation process for each frame
        self.main_simulation()

    def generate_cars(self, solution_list):
        """Generate cars from the list of solutions(neural networks) to be evaluated"""
        cars = []
        for solution in solution_list:
            cars.append(car.Car(solution, self.carStartPos[0],
                                self.carStartPos[1]))

        return cars

    def move_obstacles(self):
        """Updates position for each obstacle based on their velocity on that frame"""
        for obstacle in self.obstacles:
            # Changes position of each obstacle by their velocity
            obstacle.pos[0] += obstacle.moveX
            obstacle.pos[1] += obstacle.moveY

            # Simple algorithm to create bounce from borders by reversing direction on impact
            if obstacle.pos[0] + obstacle.radius > self.width:
                obstacle.moveX = obstacle.moveX * -1
            if obstacle.pos[0] - obstacle.radius < 0:
                obstacle.moveX = obstacle.moveX * -1
            if obstacle.pos[1] + obstacle.radius > self.height:
                obstacle.moveY = obstacle.moveY * -1
            if obstacle.pos[1] - obstacle.radius < 0:
                obstacle.moveY = obstacle.moveY * -1

    def save_solution(self, solution):
        """Save a trained solution to a file to be used later"""
        with open("trained_solution", "w") as file:
            file.write(solution.weights)

    def generate_obstacles(self):
        """Create randomly positioned objects with random velocities in Environment"""
        obstacles = []
        colour = constants.BLUE
        number_of_obstacles = random.randint(4, 9)

        # Creates obstacles with the same position near spawn on each generation to encourage cars to travel further
        position = [int(self.spawnrect[0] - 80), int(self.spawnrect[1])]
        obstacles.append(CircleObstacle(colour, position[0], position[1], [1, 0], 60))
        position = [int(self.spawnrect[0] + self.spawnrect[2] + 80), int(self.spawnrect[1])]
        obstacles.append(CircleObstacle(colour, position[0], position[1], [-1, 0], 60))

        while len(obstacles) < number_of_obstacles:
            # Generates a random  velocity
            move_x = random.randint(-3, 3)
            move_y = random.randint(-3, 3)

            # Generates a random radius
            radius = random.randint(40, 80)

            # Checks to make sure obstacles do not spawn on top of cars
            position = [random.randint(0, self.width - radius), random.randint(0, self.height - radius)]
            if not self.check_if_circle_overlaps(position[0], position[1], radius, obstacles):
                if not self.circle_rect_collision(self.spawnrect[0], self.height - self.spawnrect[1], self.spawnrect[2],
                                                  self.spawnrect[3], position[0], position[1], radius):
                    obstacles.append(CircleObstacle(colour, position[0], position[1], [move_x, move_y], radius))

        return obstacles

    @staticmethod
    def circle_rect_collision(rleft, rtop, width, height,  # rectangle definition
                              center_x, center_y, radius):  # circle definition
        """ Detect collision between a rectangle and circle. """

        dist_x = abs(center_x - rleft - width / 2)
        dist_y = abs(center_y - rtop - height / 2)

        if dist_x > (width / 2 + radius):
            return False
        if dist_y > (height / 2 + radius):
            return False

        if dist_x <= (width / 2):
            return True
        if dist_y <= (height / 2):
            return True

        dx = dist_x - width / 2
        dy = dist_y - height / 2
        return dx * dx + dy * dy <= (radius * radius)

    def check_if_circle_overlaps(self, x, y, r, other_obstacles):
        """Detects if any obstacles overlaps"""
        for obstacle in other_obstacles:
            if self.check_if_circles_overlap(x, y, r, obstacle.pos[0], obstacle.pos[1], obstacle.radius):
                return True
        return False

    def print_if_obstacles_overlap(self):
        """Returns True if any obstacles collide with another"""
        overlapping = False
        for obs in self.obstacles:
            for obst in self.obstacles:
                if obs == obst:
                    continue
                elif self.check_if_circles_overlap(obs.pos[0], obs.pos[1], obs.radius, obst.pos[0], obst.pos[1],
                                                   obst.radius):
                    overlapping = True

        print("overlapping: ", str(overlapping))

    @staticmethod
    def check_if_circles_overlap(x, y, r, a, b, t):
        """Statif function to detect if any circles overlap"""
        if math.hypot(x - a, y - b) <= (r + t):
            return True
        return False

    def create_borders(self):
        """This function creates the rectangle objects that act as borders for the screen"""
        line_width = 10
        colour = constants.RED
        width = self.width
        height = self.height

        # top line
        top = pygame.draw.rect(self.screen, colour, [0, 0, width, line_width])
        # bottom line
        bottom = pygame.draw.rect(self.screen, colour, [0, height - line_width, width, line_width])
        # left line
        left = pygame.draw.rect(self.screen, colour, [0, 0, line_width, height])
        # right line
        right = pygame.draw.rect(self.screen, colour, [width - line_width, 0, line_width, height + line_width])
        return [top, bottom, left, right]

    def set_obstacles(self):
        for car in self.cars:
            car.obstacles = self.obstacles

    def set_borders(self):
        for car in self.cars:
            car.borders = self.borders

    # Rendering of different objects in the environment by calling their draw methods
    def draw_obstacles(self):
        for obstacle in self.obstacles:
            obstacle.draw_to_screen(self.screen)

    def draw_cars(self):
        """Call the update the positions and draw each car."""
        for car in self.cars:
            car.update()
            car.draw()
        for car in self.cars:
            if car.solution.fittest:
                car.draw()

    def draw_gui(self):
        """Using the tkinter wrapper, thorpy to render the HUD."""
        gen_text = tp.OneLineText.make("Generation: " + str(self.generation_number))
        time_text = tp.OneLineText.make("Time: " + str(self.time))
        live_text = tp.OneLineText.make("Cars Alive: " + str(len(self.cars)) + "/" + str(self.pop_size))

        # Specifies font size for HUD.
        live_text.set_font_size(18)
        gen_text.set_font_size(20)
        time_text.set_font_size(20)

        # Put elements into box to manage them better.
        box = tp.Box.make(elements=[gen_text, time_text, live_text])
        menu = tp.Menu(box)

        # Render each element onto screen
        for element in menu.get_population():
            element.surface = self.screen

        box.set_topleft(((self.screen_size[0] - box.get_rect()[2]) - 10, 10))
        box.blit()

    def draw(self):
        """Calling all the draw methods"""
        self.draw_obstacles()
        self.create_borders()
        self.draw_cars()
        self.draw_gui()

    def main_simulation(self):
        """Main loop that is run after initialising Environment"""
        self.time = 0  # Stores how long the current generation has been running for.

        while self.running:
            # This is the main loop that renders each frame.
            # Each iteration involves processing and rendering data for one frame.
            self.time += 1
            for event in pygame.event.get():  # Managing the pygame event system.
                if event.type == pygame.QUIT:
                    sys.exit()  # Simple event check to close window.

            # 'Render' each frame by calculating everything until no cars left
            self.screen.fill(constants.WHITE)
            self.set_obstacles()
            self.move_obstacles()

            # Calculate data for each car
            for car in self.cars:

                # Get output decision from each car's neural network
                car.inputs = car.get_sensor_data()
                car.set_inputs(car.inputs)
                car.feed_forward()
                car.output = car.get_outputs()

                # Evaluate output and react in Environment
                if car.output == "left":
                    car.rotate_left()
                elif car.output == "right":
                    car.rotate_right()
                car.move_forward()

                # If any cars crashed, record their performance(time) and remove from Environment
                if car.crashed:
                    car.calculate_fitness(self.time)
                    car.solution.time = self.time
                    self.evaluatedCars.append(car)
                    self.cars.remove(car)

            # Terminate Environment if all cars evaluated(they crashed) or time limit reached
            if len(self.cars) == 0 or self.time > constants.TIME_LIMIT:
                for car in self.cars:
                    car.calculate_fitness(self.time)
                    car.solution.time = self.time
                    self.evaluatedCars.append(car)
                return self.cars

            # Draw current frame
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)
