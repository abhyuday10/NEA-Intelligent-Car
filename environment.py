import math
import random
import sys
import pygame
import thorpy as tp

# Initialize parameters
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)

DRAW_SENSORS = True
TIME_LIMIT = 200

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


# Car sprite to run in environment
class Car(pygame.sprite.Sprite):
    DELTA_ANGLE = 5.5
    SPEED = 5

    def __init__(self, chromosome, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.boom = pygame.image.load("boom.png")
        self.boom = pygame.transform.scale(self.boom, (50, 50))

        if chromosome.fittest:
            self.image = pygame.image.load("car_fit.png")
        else:
            self.image = pygame.image.load("car.png")

        self.image = pygame.transform.scale(self.image, (30, 60))
        self.orig_image = self.image

        self.mask = pygame.mask.from_surface(self.image)

        self.pos = [x, y]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.angle = 0
        self.crashed = False

        self.obstacles = None
        self.borders = None

        self.chromosome = chromosome

        self.inputs = None
        self.output = None

    def rotate_right(self):
        self.angle = (self.angle - self.DELTA_ANGLE) % -360

    def rotate_left(self):
        self.angle = (self.angle + self.DELTA_ANGLE) % -360

    def move_forward(self):
        dx = math.cos(math.radians(self.angle + 90))
        dy = math.sin(math.radians(self.angle + 90))

        self.pos = self.pos[0] + (dx * self.SPEED), self.pos[1] - (dy * self.SPEED)
        self.rect.center = self.pos

    # OVERRINDING DEFAULT PYGAME UPDATE FUNCTION
    def update(self):
        self.mask = pygame.mask.from_surface(self.image)
        self.crashed = self.check_if_crashed()

    def set_inputs(self, inputs):
        self.chromosome.brain.set_inputs(inputs)

    def feed_forward(self):
        self.chromosome.brain.feed_forward()

    def get_outputs(self):
        return self.chromosome.brain.get_decision()

    def calculate_fitness(self, time):
        fitness = math.pow(time, 1)
        self.chromosome.fitness = fitness

    def draw(self):
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        Game.screen.blit(self.image, self.rect)

    def check_if_crashed(self):

        sample_points = []
        outline_points = self.mask.outline()
        for i in range(len(outline_points)):
            if i % 10 == 0:
                sample_points.append(outline_points[i])

        # Samples points in car outline to check if crashed into object
        for point in sample_points:
            offsetted_mask_point = [0, 0]
            offsetted_mask_point[0] = point[0] + self.rect[0]
            offsetted_mask_point[1] = point[1] + self.rect[1]

            # Display collision sprite if crashed
            if self.check_if_point_in_any_obstacle(offsetted_mask_point) or self.check_if_point_in_any_border(
                    offsetted_mask_point):
                adjusted_rect = [offsetted_mask_point[0] - 25, offsetted_mask_point[1] - 25]
                Game.screen.blit(self.boom, adjusted_rect)
                return True
        return False

    # Function to return sensor distance to objects
    def get_arm_distance(self, arm, x, y, angle, offset):
        # Used to count the distance.
        i = 0

        # Look at each point and see if we've hit something.
        for point in arm:
            i += 1

            # Move the point to the right spot.
            rotated_p = self.get_rotated_point(
                x, y, point[0], point[1], angle + offset
            )

            # Check if we've hit something. Return the current i (distance)
            # if we did.
            if rotated_p[0] <= 0 or rotated_p[1] <= 0 \
                    or rotated_p[0] >= Game.width or rotated_p[1] >= Game.height:
                return i  # Sensor is off the screen.
            elif self.check_if_point_in_any_obstacle(rotated_p):
                return i

            elif DRAW_SENSORS:
                pygame.draw.circle(Game.screen, (BLACK), (rotated_p), 2)

        # Return the distance for the arm.
        return i

    def check_if_point_in_any_border(self, point):
        for border in self.borders:
            if self.check_inside_rect(point[0], point[1], border):
                return True
        return False

    def check_if_point_in_any_obstacle(self, point):
        for obstacle in self.obstacles:
            if self.check_inside_circle(point[0], point[1], obstacle.pos[0], obstacle.pos[1], obstacle.radius):
                return True
        return False

    # STATIC METHODS
    @staticmethod
    def check_inside_rect(x, y, rect):
        return (rect[0] + rect[2]) > x > rect[0] and (rect[1] + rect[3]) > y > rect[1]

    @staticmethod
    def check_inside_circle(x, y, a, b, r):
        return (x - a) * (x - a) + (y - b) * (y - b) < r * r

    def get_sensor_data(self):
        return self.get_sonar_readings(self.rect.center[0], self.rect.center[1], math.radians(abs(self.angle) - 90))

    def get_sonar_readings(self, x, y, angle):
        readings = []

        # Make our arms
        arm_left = self.make_sonar_arm(x, y)
        arm_middle = arm_left
        arm_right = arm_left

        # Rotate them and get readings.
        readings.append(self.get_arm_distance(arm_left, x, y, angle, 0.75))
        readings.append(self.get_arm_distance(arm_left, x, y, angle, 1.55))
        readings.append(self.get_arm_distance(arm_middle, x, y, angle, 0))
        readings.append(self.get_arm_distance(arm_left, x, y, angle, -1.55))
        readings.append(self.get_arm_distance(arm_right, x, y, angle, -0.75))

        return readings

    @staticmethod
    def make_sonar_arm(x, y):
        spread = 16  # Default spread.
        distance = 10  # Gap before first sensor.
        arm_points = []
        # Make an arm. We build it flat because we'll rotate it about the center later
        for i in range(1, 15):
            arm_points.append((distance + x + (spread * i), y))
        return arm_points

    @staticmethod
    def get_rotated_point(x_1, y_1, x_2, y_2, radians):
        # Rotate x_2, y_2 around x_1, y_1 by angle.
        x_change = (x_2 - x_1) * math.cos(radians) + \
                   (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - \
                   (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = y_change + y_1
        return int(new_x), int(new_y)


# Environment instance
class Game:
    clock = pygame.time.Clock()
    screen_size = width, height = 1200, 800
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Intelligent Driver')

    def __init__(self, chromosomeList, gen):
        self.running = True

        # Set up environment
        rectx = 200
        recty = 400
        self.spawnrect = [(self.width / 2) - rectx / 2, (self.height / 2) + recty / 20, rectx, recty]

        self.carStartPos = [self.spawnrect[0] + 100, self.spawnrect[1] + 100]

        self.obstacles = self.generate_obstacles()
        self.borders = self.create_borders()

        self.cars = self.generate_cars(chromosomeList)
        self.evaluatedCars = []

        self.generation_number = gen
        self.time = 0

        self.pop_size = len(chromosomeList)

        self.set_borders()
        self.main_loop()

    def generate_cars(self, chromosomeList):
        # Generate cars, passing in their own network
        cars = []
        for chromosome in chromosomeList:
            cars.append(Car(chromosome, self.carStartPos[0],
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

    # Create randomly positioned objects with random velocities in environment
    def generate_obstacles(self):
        obstacles = []
        colour = BLUE
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
        colour = RED
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
            if car.chromosome.fittest:
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

    # Main loop that is run after initialising environment
    def main_loop(self):
        self.time = 0

        while self.running:
            self.time += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            # 'Render' each frame by calculating everything until no cars left

            self.screen.fill(WHITE)
            self.set_obstacles()
            self.move_obstacles()

            # Calculate data for each car
            for car in self.cars:

                # Get output decision from each car's neural network
                car.inputs = car.get_sensor_data()
                car.set_inputs(car.inputs)
                car.feed_forward()
                car.output = car.get_outputs()

                # Evaluate output and react in environment
                if car.output == "left":
                    car.rotate_left()
                elif car.output == "right":
                    car.rotate_right()
                car.move_forward()

                # If any cars crashed, record their performance(time) and remove from environment
                if car.crashed:
                    car.calculate_fitness(self.time)
                    car.chromosome.time = self.time
                    self.evaluatedCars.append(car)
                    self.cars.remove(car)

            # Terminate environment if all cars evaluated(they crashed) or time limit reached
            if len(self.cars) == 0 or self.time > TIME_LIMIT:
                for car in self.cars:
                    car.calculate_fitness(self.time)
                    car.chromosome.time = self.time
                    self.evaluatedCars.append(car)
                return self.cars

            # Draw frame
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)