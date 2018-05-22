import pygame, sys
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)


class Car(pygame.sprite.Sprite):
    DELTA_ANGLE = 3
    SPEED = 5

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("car.png")
        self.image = pygame.transform.scale(self.image, (60, 120))
        self.orig_image = self.image

        self.rect = self.image.get_rect()
        self.rect[0], self.rect[1] = x, y

        self.angle = 0

    def move_right(self):
        self.rect[0] += 5

    def move_left(self):
        self.rect[0] -= 5

    def rotate_right(self):
        self.angle = (self.angle - self.DELTA_ANGLE) % -360

    def rotate_left(self):
        self.angle = (self.angle + self.DELTA_ANGLE) % -360

    def move_forward(self):
        dx = math.cos(math.radians(self.angle + 90))
        # print("dx: ",dx,"    angle: ",abs(self.angle))
        dy = math.sin(math.radians(self.angle + 90))
        # print("dy: ",dy)
        self.rect[0] += int(dx * self.SPEED)
        self.rect[1] -= int(dy * self.SPEED)
        print(int(dx * self.SPEED))
    def move_backward(self):
        dx = math.cos(math.radians(self.angle + 90))
        dy = math.sin(math.radians(self.angle + 90))

        self.rect[0] -= int(dx * self.SPEED)
        self.rect[1] += int(dy * self.SPEED)

    def displayCar(self):
        # print("Forward Angle: ",self.angle)
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        pygame.draw.rect(Game.screen, GRAY, self.rect)
        Game.screen.blit(self.image, self.rect)
        pygame.draw.circle(Game.screen, BLUE, self.rect.center, 5)

        myImage_mask = pygame.mask.from_surface(self.image)
        outline_image = pygame.Surface(self.image.get_size()).convert_alpha()
        outline_image.fill((0, 0, 0, 0))
        for point in myImage_mask.outline():
            outline_image.set_at(point, BLUE)
        Game.screen.blit(outline_image, self.rect)

        readings = self.get_sonar_readings(self.rect.center[0], self.rect.center[1], math.radians(abs(self.angle)-90))
        print(readings)
        pygame.draw.line(Game.screen, BLUE, [self.rect[0], self.rect[1]], [100, 200], 2)

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
            else:
                pygame.draw.circle(Game.screen, (BLACK), (rotated_p), 2)



        # Return the distance for the arm.
        return i

    def get_sonar_readings(self, x, y, angle):
        readings = []
        """
        Instead of using a grid of boolean(ish) sensors, sonar readings
        simply return N "distance" readings, one for each sonar
        we're simulating. The distance is a count of the first non-zero
        reading starting at the object. For instance, if the fifth sensor
        in a sonar "arm" is non-zero, then that arm returns a distance of 5.
        """
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

    def get_track_or_not(self, reading):
        if reading == THECOLORS['black']:
            return 0
        else:
            return 1

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


class Game:
    clock = pygame.time.Clock()
    screen_size = width, height = 800, 500
    screen = pygame.display.set_mode(screen_size)

    def __init__(self):
        self.car = Car(250, 200)
        self.main_loop()

    def draw(self):
        self.car.displayCar()
        self.drawObstacles()

    def drawObstacles(self):
        pygame.draw.circle(self.screen,GRAY, [250,300],50)

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

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

            self.handle_input()
            self.screen.fill(WHITE)
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)


game = Game()
