import pygame, sys

BLACK = 0, 0, 0
WHITE = 255, 255, 255
BLUE = (0, 0, 255)
GREEN = ( 0, 255, 0)
RED = (255, 0, 0)

class Car(pygame.sprite.Sprite):
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
        self.angle -= 3
    def rotate_left(self):
        self.angle += 3

        # self.image = pygame.transform.rotate(self.image, -1)
        # self.rect = self.image.get_rect(center=self.orig_rect.center)

    def displayCar(self):
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
            self.car.move_right()
        if keys[pygame.K_LEFT]:
            self.car.move_left()
        if keys[pygame.K_DOWN]:
            self.car.rotate_right()
        if keys[pygame.K_UP]:
            self.car.rotate_left()

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
