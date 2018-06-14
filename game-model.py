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


class Car(pygame.sprite.Sprite):
    DELTA_ANGLE = 2.5
    SPEED = 5

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.boom = pygame.image.load("boom.png")
        self.boom = pygame.transform.scale(self.boom, (50, 50))

        self.image = pygame.image.load("car.png")
        self.image = pygame.transform.scale(self.image, (60, 120))
        self.orig_image = self.image

        self.pos = [x, y]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.angle = 0

        self.crashed = False

        self.obstacles = None
        self.borders = None

    # def move_right(self):
    #     self.rect[0] += 5
    #
    # def move_left(self):
    #     self.rect[0] -= 5

    def rotate_right(self):
        self.angle = (self.angle - self.DELTA_ANGLE) % -360

    def rotate_left(self):
        self.angle = (self.angle + self.DELTA_ANGLE) % -360

    def move_forward(self):
        dx = math.cos(math.radians(self.angle + 90))
        dy = math.sin(math.radians(self.angle + 90))

        self.pos = self.pos[0] + (dx * self.SPEED), self.pos[1] - (dy * self.SPEED)
        self.rect.center = self.pos

    def move_backward(self):
        dx = math.cos(math.radians(self.angle + 90))
        dy = math.sin(math.radians(self.angle + 90))

        self.pos = self.pos[0] - (dx * self.SPEED), self.pos[1] + (dy * self.SPEED)
        self.rect.center = self.pos

    def displayCar(self):
        # print("Forward Angle: ",self.angle)
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # pygame.draw.rect(Game.screen, GRAY, self.rect)
        Game.screen.blit(self.image, self.rect)
        pygame.draw.circle(Game.screen, BLUE, self.rect.center, 5)

        # Calculate and display car collsion mask
        myImage_mask = pygame.mask.from_surface(self.image)
        self.mask = myImage_mask
        outline_image = pygame.Surface(self.image.get_size()).convert_alpha()
        outline_image.fill((0, 0, 0, 0))
        for point in myImage_mask.outline():
            outline_image.set_at(point, BLUE)
        Game.screen.blit(outline_image, self.rect)

        readings = self.get_sonar_readings(self.rect.center[0], self.rect.center[1], math.radians(abs(self.angle) - 90))
        # print(readings)
        pygame.draw.line(Game.screen, BLUE, [self.rect.center[0], self.rect.center[1]], [300, 300], 2)

        self.crashed = self.check_if_crashed()

    def check_if_crashed(self):
        for point in self.mask.outline():
            ofsettedMaskPoint = [0, 0]
            ofsettedMaskPoint[0] = point[0] + self.rect[0]
            ofsettedMaskPoint[1] = point[1] + self.rect[1]
            if self.check_if_point_in_any_obstacle(ofsettedMaskPoint) or self.check_if_point_in_any_border(
                    ofsettedMaskPoint):
                adjustedRect = [ofsettedMaskPoint[0] - 25, ofsettedMaskPoint[1] - 25]
                Game.screen.blit(self.boom, adjustedRect)
                # pygame.draw.circle(Game.screen, BLACK, i, 5)
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

    def get_sonar_readings(self, x, y, angle):
        readings = []

        # Make our arms.
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
        spread = 8  # Default spread.
        distance = 20  # Gap before first sensor.
        arm_points = []
        # Make an arm. We build it flat because we'll rotate it about the
        # center later.
        for i in range(1, 30):
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


class CircleObstacle():
    def __init__(self, colour, x, y, radius):
        self.colour = colour
        self.pos = [x, y]
        self.radius = radius

    def draw_to_screen(self, screen):
        pygame.draw.circle(screen, self.colour, self.pos, self.radius)


class Game:
    clock = pygame.time.Clock()
    screen_size = width, height = 800, 500
    screen = pygame.display.set_mode(screen_size)

    def __init__(self):
        self.car = Car(250, 200)

        print("created obstacles")
        self.obstacles = self.generateObstacles()
        self.car.obstacles = self.obstacles

        self.car.borders = self.drawBorder()
        self.main_loop()

    def check_if_circles_overlap(self, x, y, r, a, b, t):
        if math.hypot(x - a, y - b) <= (r + t):
            return True
        return False

    def generateObstacles(self):
        obstacles = []
        overlapping = False
        colour = BLUE
        for i in range(random.randint(4, 7)):
            radius = random.randint(40, 90)
            position = [random.randint(0, self.width - radius), random.randint(0, self.height - radius)]
            obstacles.append(CircleObstacle(colour, position[0], position[1], radius))

        for obs in obstacles:
            for obst in obstacles:
                if obs == obst:
                    continue
                elif self.check_if_circles_overlap(obs.pos[0], obs.pos[1], obs.radius, obst.pos[0], obst.pos[1],
                                                   obst.radius):
                    overlapping = True
        print("overlapping: ", str(overlapping))
        return obstacles

    def draw(self):

        self.drawObstacles()
        self.car.displayCar()
        self.drawBorder()

    def drawBorder(self):
        # top line
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

    def drawObstacles(self):
        for obstacle in self.obstacles:
            obstacle.draw_to_screen(self.screen)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.car.rotate_right()
        if keys[pygame.K_LEFT]:
            self.car.rotate_left()
        if keys[pygame.K_DOWN]:
            self.car.move_backward()
        if keys[pygame.K_UP]:
            self.car.move_forward()

    def main_loop(self):

        while not self.car.crashed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

            self.handle_input()
            self.screen.fill(WHITE)
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)


game = Game()
