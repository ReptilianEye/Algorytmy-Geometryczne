import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


class myPlot:
    def __init__(self) -> None:
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig = fig
        # ax = plt.axes(autoscale_on=False)
        self.ax = ax
        self.prev_points = []
        self.lines = []
        self.autoscaling = False

    def reset(self, event):
        self.prev_point = []
        self.lines = []
        self.draw()

    def print_segments(self, event):
        if len(self.lines) == 0:
            print("Nie ma zapisanych odcinków")

        for line in self.lines:
            print((line.get_xdata(), line.get_ydata()))

    def undo(self, event):
        if len(self.prev_points) == 0:
            return

        if len(self.prev_points) > 1:
            self.lines.pop()
        self.prev_points.pop()
        self.draw()

    def add_point(self, point):
        self.prev_points.append(point)

    def add_line(self, line):
        self.lines.append(line)

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        x, y = event.xdata, event.ydata
        if len(self.prev_points) in [0, 2]:
            self.prev_points = []
            self.add_point([x, y])
        else:
            p1 = self.prev_points[-1]
            p2 = [x, y]
            # Create a line using x and y coordinates
            self.add_line(plt.Line2D([p1[0], p2[0]], [p1[1], p2[1]]))
            self.add_point(p2)
        self.draw()

    def draw(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.clear()
        if len(self.prev_points) > 0:
            point = self.prev_points[-1]
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


myplot = myPlot()
fig = myplot.fig


# # create buttons
button_y = 0.05
button_width = 0.2
button_height = 0.1
button_n = 3
button_pos = [[i*button_width*1.1+0.1, button_y, button_width,
               button_height] for i in range(button_n)]
axes = [fig.add_axes(pos) for pos in button_pos]
bundo = Button(axes[0], 'Undo')
bundo.on_clicked(myplot.undo)
bprint = Button(axes[1], 'Print segments')
bprint.on_clicked(myplot.print_segments)
breset = Button(axes[2], 'Reset')
breset.on_clicked(myplot.reset)

myplot.show()
