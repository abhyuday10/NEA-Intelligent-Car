import math
import random
import sys

import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)


class CircleObstacle():
    def __init__(self, colour, x, y, move, radius):
        self.moveX = move[0]
        self.moveY = move[1]

        self.colour = colour
        self.pos = [x, y]
        self.radius = radius

    def draw_to_screen(self, screen):
        pygame.draw.circle(screen, self.colour, self.pos, self.radius)


class Car(pygame.sprite.Sprite):
    DELTA_ANGLE = 3.5
    SPEED = 5

    def __init__(self, chromosome, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.boom = pygame.image.load("boom.png").convert_alpha()
        self.boom = pygame.transform.scale(self.boom, (50, 50))

        self.image = pygame.image.load("car.png").convert_alpha()
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

    def update(self):
        self.inputs = self.get_sonar_readings(self.rect.center[0], self.rect.center[1],
                                              math.radians(abs(self.angle) - 90))
        self.mask = pygame.mask.from_surface(self.image)
        self.crashed = self.check_if_crashed()

    def set_inputs(self, inputs):
        self.chromosome.brain.setInputs(inputs)

    def feedforward(self):
        self.chromosome.brain.feedForward()

    def get_outputs(self):
        return self.chromosome.brain.getDiscreteResults()

    def calculate_fitness(self, time):
        fitness = math.pow(time, 2)
        self.chromosome.fitness = fitness

    def draw(self):
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        Game.screen.blit(self.image, self.rect)

    def check_if_crashed(self):

        samplePoints = []
        outlinePoints = self.mask.outline()
        for i in range(len(outlinePoints)):
            if i % 10 == 0:
                samplePoints.append(outlinePoints[i])

        # for point in samplePoints:
        #     self.image.set_at(point, BLACK)

        for point in samplePoints:
            ofsettedMaskPoint = [0, 0]
            ofsettedMaskPoint[0] = point[0] + self.rect[0]
            ofsettedMaskPoint[1] = point[1] + self.rect[1]

            # pygame.draw.circle(Game.screen, GREEN, ofsettedMaskPoint, 2)

            if self.check_if_point_in_any_obstacle(ofsettedMaskPoint) or self.check_if_point_in_any_border(
                    ofsettedMaskPoint):
                adjustedRect = [ofsettedMaskPoint[0] - 25, ofsettedMaskPoint[1] - 25]
                Game.screen.blit(self.boom, adjustedRect)
                # pygame.draw.circle(Game.screen, RED, ofsettedMaskPoint, 5)
                return True
        return False

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

            else:
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

    def check_inside_rect(self, x, y, rect):
        return (rect[0] + rect[2]) > x > rect[0] and (rect[1] + rect[3]) > y > rect[1]

    def check_inside_circle(self, x, y, a, b, r):
        return (x - a) * (x - a) + (y - b) * (y - b) < r * r

    def get_sensor_data(self):
        return self.get_sonar_readings(self.rect.center[0], self.rect.center[1], math.radians(abs(self.angle) - 90))

    def get_sonar_readings(self, x, y, angle):
        readings = []

        # Make our arms.Capi
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

    def make_sonar_arm(self, x, y):
        spread = 16  # Default spread.
        distance = 20  # Gap before first sensor.
        arm_points = []
        # Make an arm. We build it flat because we'll rotate it about the
        # center later.
        for i in range(1, 15):
            arm_points.append((distance + x + (spread * i), y))
        return arm_points

    def get_rotated_point(self, x_1, y_1, x_2, y_2, radians):
        # Rotate x_2, y_2 around x_1, y_1 by angle.
        x_change = (x_2 - x_1) * math.cos(radians) + \
                   (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - \
                   (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = y_change + y_1
        return int(new_x), int(new_y)


class Game:
    clock = pygame.time.Clock()
    screen_size = width, height = 1200, 800
    screen = pygame.display.set_mode(screen_size)

    def __init__(self, chromosomeList):
        self.running = True

        rectx = 200
        recty = 400
        self.spawnrect = [(self.width / 2) - rectx / 2, (self.height / 2) + recty / 20, rectx, recty]

        self.carStartPos = [self.spawnrect[0] + 100, self.spawnrect[1] + 100]
        # self.carStartPos = [random.randint(self.spawnrect[0], self.spawnrect[0] + self.spawnrect[2]),
        #                     self.spawnrect[1] + 100]
        # print(self.carStartPos)

        self.obstacles = self.generateObstacles()
        self.borders = self.createBorders()

        self.cars = self.generateCars(chromosomeList)
        self.evaluatedCars = []

        self.set_borders()
        self.main_loop()

    def generateCars(self, chromosomeList):
        # Generate cars, passing in their unique network
        cars = []
        for chromosome in chromosomeList:
            cars.append(Car(chromosome, self.carStartPos[0],
                            self.carStartPos[1]))

        return cars

    def moveObstacles(self):

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

    def generateObstacles(self):
        obstacles = []
        colour = BLUE
        numberofObstacles = random.randint(3, 7)

        position = [int(self.spawnrect[0] - 80), int(self.spawnrect[1])]
        obstacles.append(CircleObstacle(colour, position[0], position[1], [0, 0], 60))

        position = [int(self.spawnrect[0] + self.spawnrect[2] + 80), int(self.spawnrect[1])]
        obstacles.append(CircleObstacle(colour, position[0], position[1], [0, 0], 60))

        while len(obstacles) < numberofObstacles:

            moveX = random.randint(-3, 3)
            moveY = random.randint(-3, 3)

            radius = random.randint(40, 80)
            position = [random.randint(0, self.width - radius), random.randint(0, self.height - radius)]
            if not self.check_if_circle_overlaps(position[0], position[1], radius, obstacles):
                if not self.circle_rect_collision(self.spawnrect[0], self.height - self.spawnrect[1], self.spawnrect[2],
                                                  self.spawnrect[3], position[0], position[1], radius):
                    obstacles.append(CircleObstacle(colour, position[0], position[1], [moveX, moveY], radius))

        return obstacles

    def circle_rect_collision(self, rleft, rtop, width, height,  # rectangle definition
                              center_x, center_y, radius):  # circle definition
        """ Detect collision between a rectangle and circle. """

        distX = abs(center_x - rleft - width / 2)
        distY = abs(center_y - rtop - height / 2)

        if (distX > (width / 2 + radius)):
            return False
        if (distY > (height / 2 + radius)):
            return False

        if (distX <= (width / 2)):
            return True
        if (distY <= (height / 2)):
            return True

        dx = distX - width / 2
        dy = distY - height / 2
        return (dx * dx + dy * dy <= (radius * radius))

    def check_if_circle_overlaps(self, x, y, r, other_obstacles):
        for obstacle in other_obstacles:
            if self.check_if_circles_overlap(x, y, r, obstacle.pos[0], obstacle.pos[1], obstacle.radius):
                return True
        return False

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

    def check_if_circles_overlap(self, x, y, r, a, b, t):
        if math.hypot(x - a, y - b) <= (r + t):
            return True
        return False

    def createBorders(self):
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

    def drawObstacles(self):
        for obstacle in self.obstacles:
            obstacle.draw_to_screen(self.screen)

    def draw_cars(self):
        for car in self.cars:
            car.update()
            car.draw()

    def draw(self):
        # pygame.draw.rect(self.screen, GRAY, self.spawnrect)
        self.drawObstacles()
        self.createBorders()
        self.draw_cars()

    def main_loop(self):
        time = 0
        while self.running:
            time += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

            # Each Frame
            self.screen.fill(WHITE)

            self.set_obstacles()
            self.moveObstacles()

            # print(len(self.cars))

            for car in self.cars:
                car.inputs = car.get_sensor_data()
                car.set_inputs(car.inputs)
                car.feedforward()
                car.output = car.get_outputs()
                # print(car.chromosome.brain.getResults())
            # print(" ")

            for car in self.cars:
                if car.output == "left":
                    car.rotate_left()
                elif car.output == "right":
                    car.rotate_right()
                car.move_forward()

            for car in self.cars:
                if car.crashed:
                    car.calculate_fitness(time)
                    car.chromosome.time = time
                    self.evaluatedCars.append(car)
                    self.cars.remove(car)

            if len(self.cars) == 0 or time > 820:
                for car in self.cars:
                    car.calculate_fitness(time)
                    car.chromosome.time = time
                    self.evaluatedCars.append(car)
                return self.cars

            self.draw()
            # self.draw()

            # Do all drawing and stuff here:
            # set obstacles for cars
            # initial draw
            # get sensor data: set brain inputs --->
            # evaluate car outputs; move cars; draw everything; test collision
            # for each:
            # if no crash: repeat
            # else: set car crash=True, calc fitness, remove from pop
            # DO until no cars left
            # .....GA evaluation, new pop repeat

            pygame.display.flip()
            self.clock.tick(60)

# Game([])
