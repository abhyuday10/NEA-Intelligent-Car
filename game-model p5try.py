from p5 import *

class Game:
    def __init__(self):

        self.car=Car(100, 200)
        self.setup()

    def setup(self):
        size(800, 500)
        no_stroke()
        background(204)
        while True:
            self.draw()


    def draw(self):
        print("drawing")
        background(255)
        self.car.displayCar()

    def key_pressed(self,event):
        if event.key == "RIGHT":
            self.car.move_right()


class Car():
    xPos = None
    yPos = None
    carColour = 0

    def __init__(self, x, y):
        self.xPos = x
        self.yPos = y

    def move_right(self):
        self.xPos += 5

    def displayCar(self):
        no_stroke()
        fill(self.carColour)
        rect((self.xPos, self.yPos), 50, 75)







game=Game()
run()
