import pygame
import math
import environment as env
import constants

# Car sprite to run in Environment
class Car(pygame.sprite.Sprite):
    DELTA_ANGLE = 5.5
    SPEED = 5

    def __init__(self, solution, x, y):

        pygame.sprite.Sprite.__init__(self)

        self.boom = pygame.image.load("images/explosion.png")
        self.boom = pygame.transform.scale(self.boom, (50, 50))

        if solution.fittest:
            self.image = pygame.image.load("images/car_fit.png")
        else:
            self.image = pygame.image.load("images/car.png")

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

        self.solution = solution

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
        self.solution.brain.set_inputs(inputs)

    def feed_forward(self):
        self.solution.brain.feed_forward()

    def get_outputs(self):
        return self.solution.brain.get_decision()

    def calculate_fitness(self, time):
        fitness = math.pow(time, 1)
        self.solution.fitness = fitness

    def draw(self):
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        env.Environment.screen.blit(self.image, self.rect)

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
                env.Environment.screen.blit(self.boom, adjusted_rect)
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
                    or rotated_p[0] >= env.Environment.width or rotated_p[1] >= env.Environment.height:
                return i  # Sensor is off the screen.
            elif self.check_if_point_in_any_obstacle(rotated_p):
                return i

            elif constants.DRAW_SENSORS:
                pygame.draw.circle(env.Environment.screen, constants.BLACK, rotated_p, 2)

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
        return self.get_sensor_readings(self.rect.center[0], self.rect.center[1], math.radians(abs(self.angle) - 90))

    def get_sensor_readings(self, x, y, angle):
        readings = []

        # Make our arms
        arm_left = self.make_sensor_arm(x, y)
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
    def make_sensor_arm(x, y):
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
