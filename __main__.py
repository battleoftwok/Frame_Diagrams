from abc import ABC, abstractmethod
from tkinter import *
from math import *

WIDTH, HEIGHT = 820, 820
DIAPASON = 0, 181
AMOUNT = 1
RADIUS_SCALE_FACTOR = 100
P = 780
r = 1.35
H = 29670
T = 172

SCALE_FACTOR = 0.005


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

    @staticmethod
    def scaling(coordinates):
        return coordinates[0] + RADIUS_SCALE_FACTOR * r, coordinates[1]

    @property
    def radian_angle_diapason(self):
        return (angle * pi / 180 for angle in range(*DIAPASON, AMOUNT))


class M_sum_DiagramStrategy(PolarDiagramStrategy):
    name = "ЭM𝛴"

    def __call__(self, scale_factor, *args, **kwargs):
        polar_coords = ([RADIUS_SCALE_FACTOR * r + scale_factor *
                         (-H / (2 * pi) * (2 * angle * sin(angle) - angle)), angle]
                        for angle in self.radian_angle_diapason)

        return (self.convert_coords(coordinates) for coordinates in polar_coords)


class Q_DiagramStrategy(PolarDiagramStrategy):
    name = "ЭQ"

    def __call__(self, scale_factor, *args, **kwargs):
        polar_coords = ((RADIUS_SCALE_FACTOR * r + scale_factor * (-H / (2 * pi * r) * (2 * cos(angle) - 1)), angle)
                        for angle in self.radian_angle_diapason)

        return (self.convert_coords(coordinates) for coordinates in polar_coords)


class N_DiagramStrategy(PolarDiagramStrategy):
    name = "ЭN"

    def __call__(self, scale_factor, *args, **kwargs):
        polar_coords = ((RADIUS_SCALE_FACTOR * r + scale_factor * (H / (pi * r) * sin(angle)), angle)
                        for angle in self.radian_angle_diapason)

        return (self.convert_coords(coordinates) for coordinates in polar_coords)


class Painter:
    def __init__(self, diagram: PolarDiagramStrategy, canvas: Canvas):
        self.canvas = canvas
        self.diagram = diagram

        self.canvas_width = int(self.canvas['width'])  # ширина полотна
        self.canvas_height = int(self.canvas['height'])  # высота полотна

    def draw_frame(self):
        self.canvas.create_oval(self.canvas_width // 2 - RADIUS_SCALE_FACTOR * r,
                                self.canvas_height // 2 - RADIUS_SCALE_FACTOR * r,
                                self.canvas_width // 2 + RADIUS_SCALE_FACTOR * r,
                                self.canvas_height // 2 + RADIUS_SCALE_FACTOR * r,
                                width=4, outline='black')

        self.canvas.create_line(self.canvas_width // 2, 0, self.canvas_width // 2, self.canvas_height)
        self.canvas.create_line(0, self.canvas_height // 2, self.canvas_width, self.canvas_height // 2)

    def draw_line(self, scale_factor):
        return self.canvas.create_line(*self.diagram(scale_factor), fill='red', width=2)

    def draw_sticks(self, scale_factor):
        for coords, angle in zip(reversed(list(self.diagram(scale_factor))), self.diagram.radian_angle_diapason):
            self.canvas.create_line(-RADIUS_SCALE_FACTOR * r * cos(angle) + self.canvas_width // 2,
                                    -RADIUS_SCALE_FACTOR * r * sin(angle) + self.canvas_height // 2,
                                    coords[0], coords[1], fill='red', width=2)


class App:
    all_diagrams = [M_sum_DiagramStrategy(WIDTH, HEIGHT, 100, 90),
                    N_DiagramStrategy(WIDTH, HEIGHT, 100, 90), Q_DiagramStrategy(WIDTH, HEIGHT, 100, 90)]

    factor = 0

    change_number = None

    def __init__(self):

        self.root = Tk()
        self.root.title("Практическое занятие №2. Вариант 1")
        self.canvas = Canvas(self.root, width=WIDTH, height=HEIGHT, bg='white')

        self.painter = Painter(self.all_diagrams[0], self.canvas)

        self.scale = Scale(self.root, from_=-1, to=1, length=700,
                           resolution=0.001, orient=HORIZONTAL, command=self.change_parameter)

        self.scale_two = Scale(self.root, from_=100, to=250, length=700,
                               resolution=1, orient=HORIZONTAL, command=self.change_parameter_two)

        self.scale.pack()
        self.scale_two.pack()

        self.choose_strategy(0)
        self.choose_strategy(1)

        self.root.bind("0", lambda event: self.choose_strategy(0))
        self.root.bind("1", lambda event: self.choose_strategy(1))
        self.root.bind("2", lambda event: self.choose_strategy(2))

    def change_parameter(self, val):
        self.factor = float(val) / 50
        self.choose_strategy(self.change_number)

    def change_parameter_two(self, val):
        global RADIUS_SCALE_FACTOR

        RADIUS_SCALE_FACTOR = float(val)
        self.choose_strategy(self.change_number)

    def choose_strategy(self, number):
        self.change_number = number
        self.clean_canvas()
        strategy = self.all_diagrams[number]
        self.painter = Painter(strategy, self.canvas)
        self.painter.draw_sticks(self.factor)
        self.painter.draw_line(self.factor)
        self.canvas.create_text(150, 50, text=strategy.name,
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
