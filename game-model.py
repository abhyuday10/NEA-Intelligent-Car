import pygame, sys
import math

BLACK = 0, 0, 0
WHITE = 255, 255, 255
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Car(pygame.sprite.Sprite):
    DELTA_ANGLE = 3
    SPEED = 5

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("car.png")
        self.image = pygame.transform.scale(self.image, (50, 100))
        self.orig_image = self.image

        self.rect = self.image.get_rect()
        self.rect[0], self.rect[1] = x, y

        self.angle = 0

    def move_right(self):
        self.rect[0] += 5

    def move_left(self):
        self.rect[0] -= 5

    def rotate_right(self):
        self.angle = (self.angle-self.DELTA_ANGLE)%-360

    def rotate_left(self):
        self.angle = (self.angle + self.DELTA_ANGLE)%-360

    def move_forward(self):
        dx = math.cos(math.radians(self.angle+90))
        dy = math.sin(math.radians(self.angle+90))

        self.rect[0] += dx * self.SPEED
        self.rect[1] -= dy * self.SPEED

    def move_backward(self):
        dx = math.cos(math.radians(self.angle + 90))
        dy = math.sin(math.radians(self.angle + 90))

        self.rect[0] -= dx * self.SPEED
        self.rect[1] += dy * self.SPEED



    def displayCar(self):
        print(-self.angle)
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        pygame.draw.rect(Game.screen, BLACK, self.rect)
        Game.screen.blit(self.image, self.rect)
        pygame.draw.circle(Game.screen, BLUE, self.rect.center, 5)


class Game:
    clock = pygame.time.Clock()
    screen_size = width, height = 800, 500
    screen = pygame.display.set_mode(screen_size)

    def __init__(self):
        self.car = Car(250, 200)
        self.main_loop()

    def draw(self):
        self.car.displayCar()

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
