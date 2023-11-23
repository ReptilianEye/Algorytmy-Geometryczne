import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


def dist(point1, point2):
    return np.sqrt(np.power(point1[0] - point2[0], 2) + np.power(point1[1] - point2[1], 2))


TOLERANCE = 0.01


def create_buttons(callback):
    button_y = 0.05
    button_width = 0.2
    button_height = 0.1
    button_n = 3
    button_pos = [[1-(i+1.5)*button_width, button_y, button_width,
                   button_height] for i in range(button_n)]
    # axprev = fig.add_axes([0.7, button_y, button_width, button_height])
    # axnext = fig.add_axes([0.01, 0.05, 0.1, 0.175])  # lewo gora szerokosc wysokosc
    axes = [callback.fig.add_axes(pos) for pos in button_pos]
    bnext = Button(axes[0], 'Reset')
    bnext.on_clicked(callback.reset)
    bprev = Button(axes[1], 'Print polygons')
    bprev.on_clicked(callback.print_polygons)
    btest = Button(axes[2], 'Add new')
    btest.on_clicked(callback.add_new_polygon)


class myPlot:
    def __init__(self, polygon=None) -> None:
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig = fig
        # ax = plt.axes(autoscale_on=False)
        self.ax = ax
        self.points = []
        self.lines = []
        self.polygons = []
        self.autoscaling = False
        if polygon is not None:
            self.load_polygon(polygon)

        self.closed = False
        # self.create_buttons()

    def load_polygon(self, polygon):
        self.polygons.append(polygon)
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i+1) % len(polygon)]
            self.add_line(plt.Line2D([p1[0], p2[0]], [p1[1], p2[1]]))
            self.add_point(p2)
        self.closed = True
        self.autoscaling = True
        self.draw()

    def reset(self, event):
        self.add_new_polygon(event)
        self.polygons = []
        self.draw()

    def print_polygons(self, event):
        if len(self.polygons) == 0:
            print("Nie ma zapisanych wielokątów")

        for polygon in self.polygons:
            print(polygon)

    def add_new_polygon(self, event):
        self.points = []
        self.lines = []
        self.closed = False
        self.autoscaling = False
        self.draw()

    def undo(self, event):
        if len(self.points) > 0:
            self.points.pop()
        if len(self.lines) > 0:
            self.lines.pop()
        if self.closed:
            self.closed = False
            if len(self.polygons) > 0:
                self.polygons.pop()

        self.draw()

    def add_point(self, point):
        self.points.append(point)

    def add_line(self, line):
        self.lines.append(line)

    def close_polygon(self, event):
        x = event.xdata
        y = event.ydata
        for point in self.points:
            if dist(point, [x, y]) < TOLERANCE:
                self.closed = True
                return point
        return x, y

    def save_polygon(self):
        lines = self.lines
        polygon = []
        for line in lines:
            polygon.append(
                np.array([line.get_xdata()[0], line.get_ydata()[0]]))

        self.polygons.append(polygon)
        print(polygon)

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        x, y = self.close_polygon(event)
        if len(self.points) == 0 or self.closed:
            self.add_point([x, y])
        else:
            p1 = self.points[-1]
            p2 = [x, y]
            # Create a line using x and y coordinates
            self.add_line(plt.Line2D([p1[0], p2[0]], [p1[1], p2[1]]))
            self.add_point(p2)
        if self.closed:
            self.save_polygon()
        self.draw()

    def draw(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.clear()
        if len(self.points) > 0:
            point = self.points[-1]
            self.ax.scatter(point[0], point[1], color='black')
        for line in self.lines:
            self.ax.add_line(line)
        self.ax.autoscale(self.autoscaling)
        if not self.autoscaling:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        plt.draw()

    def show(self):
        plt.show()


polygon_example_1 = [(5, 5), (3, 4), (6, 3), (4, 2), (6, 0), (7, 1), (8, 4)]
myplot = myPlot(polygon_example_1)
fig = myplot.fig


# # create buttons
button_y = 0.05
button_width = 0.2
button_height = 0.1
button_n = 4
button_pos = [[i*button_width*1.1+0.1, button_y, button_width,
               button_height] for i in range(button_n)]
axes = [fig.add_axes(pos) for pos in button_pos]
bundo = Button(axes[0], 'Undo')
bundo.on_clicked(myplot.undo)
bnew = Button(axes[1], 'Add new')
bnew.on_clicked(myplot.add_new_polygon)
bprint = Button(axes[2], 'Print polygons')
bprint.on_clicked(myplot.print_polygons)
breset = Button(axes[3], 'Reset')
breset.on_clicked(myplot.reset)

myplot.show()
