from abc import ABC, abstractmethod
from tkinter import *
from math import *

WIDTH, HEIGHT = 820, 820
DIAPASON = 0, 185
AMOUNT = 5
FACTOR = 350
P = 780
r = 0.68
H = 124.8


class DiagramStrategy(ABC):
    name = ""

    @abstractmethod
    def convert_coords(self, coordinates):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def __init__(self, width, height, moment_value, point):
        self.height = height
        self.width = width
        self.moment_value = moment_value
        self.point = point


class PolarDiagramStrategy(DiagramStrategy, ABC):

    def convert_coords(self, coordinates):
        return coordinates[0] * cos(coordinates[1]) + self.width // 2, \
               -coordinates[0] * sin(coordinates[1]) + self.height // 2

    @property
    def radian_angle_diapason(self):
        return (angle * pi / 180 for angle in range(*DIAPASON, AMOUNT))


class M_sum_DiagramStrategy(PolarDiagramStrategy):
    name = "ЭM𝛴"

    def __call__(self, *args, **kwargs):
        polar_coords = ([FACTOR * r + ((P*r) / (2 * pi) * (1 - angle * sin(angle) - .5*cos(angle))), angle]
                        for angle in self.radian_angle_diapason)

        return (self.convert_coords(coordinates) for coordinates in polar_coords)


class Q_DiagramStrategy(PolarDiagramStrategy):
    name = "ЭQ"

    def __call__(self, *args, **kwargs):
        polar_coords = ((FACTOR * r + (-P / (2 * pi) * (angle*cos(angle) + .5*sin(angle))), angle)
                        for angle in self.radian_angle_diapason)

        return (self.convert_coords(coordinates) for coordinates in polar_coords)


class N_DiagramStrategy(PolarDiagramStrategy):
    name = "ЭN"

    def __call__(self, *args, **kwargs):
        polar_coords = ((FACTOR * r + .8*(-P / (pi * 2)*(3/2*cos(angle)+angle*sin(angle))), angle)
                        for angle in self.radian_angle_diapason)

        return (self.convert_coords(coordinates) for coordinates in polar_coords)


class Painter:
    def __init__(self, diagram: PolarDiagramStrategy, canvas: Canvas):
        self.canvas = canvas
        self.diagram = diagram

        self.canvas_width = int(self.canvas['width'])  # ширина полотна
        self.canvas_height = int(self.canvas['height'])  # высота полотна

    def draw_frame(self):
        self.canvas.create_oval(self.canvas_width // 2 - FACTOR * r, self.canvas_height // 2 - FACTOR * r,
                                self.canvas_width // 2 + FACTOR * r, self.canvas_height // 2 + FACTOR * r,
                                width=4, outline='black')

        self.canvas.create_line(self.canvas_width // 2, 0, self.canvas_width//2, self.canvas_height)
        self.canvas.create_line(0, self.canvas_height//2, self.canvas_width, self.canvas_height//2)

    def draw_line(self):
        return self.canvas.create_line(*self.diagram(), fill='red', width=2)

    def draw_sticks(self):
        for coords, angle in zip(reversed(list(self.diagram())), self.diagram.radian_angle_diapason):
            self.canvas.create_line(-FACTOR * r * cos(angle) + self.canvas_width // 2,
                                    -FACTOR * r * sin(angle) + self.canvas_height // 2,
                                    coords[0], coords[1], fill='red', width=2)


class App:
    all_diagrams = [M_sum_DiagramStrategy(WIDTH, HEIGHT, 100, 90),
                    N_DiagramStrategy(WIDTH, HEIGHT, 100, 90), Q_DiagramStrategy(WIDTH, HEIGHT, 100, 90)]

    def __init__(self):
        # self.var = IntVar()
        self.root = Tk()
        self.root.title("Практическое занятие №2. Вариант 1")
        self.canvas = Canvas(self.root, width=WIDTH, height=HEIGHT, bg='white')

        self.painter = Painter(self.all_diagrams[0], self.canvas)
        self.choose_strategy(0)

        self.root.bind("0", lambda event: self.choose_strategy(0))
        self.root.bind("1", lambda event: self.choose_strategy(1))
        self.root.bind("2", lambda event: self.choose_strategy(2))

    def choose_strategy(self, number):
        self.clean_canvas()
        strategy = self.all_diagrams[number]
        self.painter = Painter(strategy, self.canvas)
        self.painter.draw_sticks()
        self.painter.draw_line()
        self.canvas.create_text(150, 50, text="Эпюра " + strategy.name,
                                font=('Times', 30, 'bold italic'), fill='black')

    def clean_canvas(self):
        self.canvas.delete(ALL)
        self.painter.draw_frame()

    def run(self):
        self.canvas.pack()
        self.root.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()
