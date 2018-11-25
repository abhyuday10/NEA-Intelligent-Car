import math
import random
import sys

import pygame
import thorpy as tp

import constants
from car import Car

# Initialize pygame
pygame.init()


# Circular obstacle
class CircleObstacle:
    def __init__(self, colour, x, y, move, radius):
        self.moveX = move[0]
        self.moveY = move[1]

        self.colour = colour
        self.pos = [x, y]
        self.radius = radius

    def draw_to_screen(self, screen):
        pygame.draw.circle(screen, self.colour, self.pos, self.radius)




# Environment instance
class Environment:
    clock = pygame.time.Clock()
    screen_size = width, height = 1200, 800
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Intelligent Driver')

    def __init__(self, solution_list, gen):
        self.running = True

        # Set up Environment
        rectx = 200
        recty = 400
        self.spawnrect = [(self.width / 2) - rectx / 2, (self.height / 2) + recty / 20, rectx, recty]

        self.carStartPos = [self.spawnrect[0] + 100, self.spawnrect[1] + 100]

        self.obstacles = self.generate_obstacles()
        self.borders = self.create_borders()

        self.cars = self.generate_cars(solution_list)
        self.evaluatedCars = []

        self.generation_number = gen
        self.time = 0

        self.pop_size = len(solution_list)

        self.set_borders()
        self.main_simulation()

    def generate_cars(self, solution_list):
        # Generate cars, passing in their own network
        cars = []
        for solution in solution_list:
            cars.append(Car(solution, self.carStartPos[0],
                            self.carStartPos[1]))

        return cars

    def move_obstacles(self):
        # Update position for each obstacle based on their velocity
        for obstacle in self.obstacles:
            obstacle.pos[0] += obstacle.moveX
            obstacle.pos[1] += obstacle.moveY

            if obstacle.pos[0] + obstacle.radius > self.width:
                obstacle.moveX = obstacle.moveX * -1
            if obstacle.pos[0] - obstacle.radius < 0:
                obstacle.moveX = obstacle.moveX * -1
            if obstacle.pos[1] + obstacle.radius > self.height:
                obstacle.moveY = obstacle.moveY * -1
            if obstacle.pos[1] - obstacle.radius < 0:
                obstacle.moveY = obstacle.moveY * -1

    # Create randomly positioned objects with random velocities in Environment
    def generate_obstacles(self):
        obstacles = []
        colour = constants.BLUE
        number_of_obstacles = random.randint(4, 9)

        position = [int(self.spawnrect[0] - 80), int(self.spawnrect[1])]
        obstacles.append(CircleObstacle(colour, position[0], position[1], [1, 0], 60))

        position = [int(self.spawnrect[0] + self.spawnrect[2] + 80), int(self.spawnrect[1])]
        obstacles.append(CircleObstacle(colour, position[0], position[1], [-1, 0], 60))

        while len(obstacles) < number_of_obstacles:

            move_x = random.randint(-3, 3)
            move_y = random.randint(-3, 3)

            radius = random.randint(40, 80)
            # Only spawn if doesn't create obstacle on car
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
        for obstacle in other_obstacles:
            if self.check_if_circles_overlap(x, y, r, obstacle.pos[0], obstacle.pos[1], obstacle.radius):
                return True
        return False

    # Check if any obstacles collide
    def print_if_obstacles_overlap(self):
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
        if math.hypot(x - a, y - b) <= (r + t):
            return True
        return False

    def create_borders(self):
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

    def draw_obstacles(self):
        for obstacle in self.obstacles:
            obstacle.draw_to_screen(self.screen)

    def draw_cars(self):
        for car in self.cars:
            car.update()
            car.draw()
        for car in self.cars:
            if car.solution.fittest:
                car.draw()

    def draw_gui(self):
        gen_text = tp.OneLineText.make("Generation: " + str(self.generation_number))
        time_text = tp.OneLineText.make("Time: " + str(self.time))
        live_text = tp.OneLineText.make("Cars Alive: " + str(len(self.cars)) + "/" + str(self.pop_size))

        live_text.set_font_size(18)
        gen_text.set_font_size(20)
        time_text.set_font_size(20)

        box = tp.Box.make(elements=[gen_text, time_text, live_text])
        menu = tp.Menu(box)

        for element in menu.get_population():
            element.surface = self.screen

        box.set_topleft(((self.screen_size[0] - box.get_rect()[2]) - 10, 10))
        box.blit()

    def draw(self):
        self.draw_obstacles()
        self.create_borders()
        self.draw_cars()
        self.draw_gui()

    # Main loop that is run after initialising Environment
    def main_simulation(self):
        self.time = 0

        while self.running:
            self.time += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

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

            # Draw frame
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)