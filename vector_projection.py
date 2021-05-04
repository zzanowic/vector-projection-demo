import tkinter as tk
import math


class App(tk.Tk):
    p_line_x = 0
    p_line_y = 0

    def __init__(self):
        super().__init__()
        self.title('Vector Projection Demo')

        self.canvas = tk.Canvas(master=self, width=500, height=500, background='black')
        self.canvas.pack(side=tk.LEFT)

        self.canvas.bind('<ButtonPress-1>', self.lButtonDown)
        self.canvas.bind('<ButtonPress-2>', self.rButtonDown)
        self.canvas.bind('<Motion>', self.mouseMove)

        frame = tk.Frame(master=self)
        frame.pack(side=tk.LEFT)

        label1 = tk.Label(master=frame, text='Left mouse sets the vector\nRight mouse sets projection line', width=30)
        label1.pack()

        self.text2 = tk.StringVar()
        label2 = tk.Label(master=frame, textvariable=self.text2)
        label2.pack()

        self.text3 = tk.StringVar()
        label3 = tk.Label(master=frame, textvariable=self.text3)
        label3.pack()

        self.projection_line = Line(self)
        self.projection_line.setVector(0, 0, 500, 500)
        self.line1 = Line(self, arrow='last')
        self.line1.setVector(50, 300, 100, 0)
        self.line1_1 = Line(self, 'light gray', dash=5)
        self.line1_2 = Line(self, 'light gray', dash=5)
        self.line1_projection = Line(self, 'red', arrow='last')
        self.line1_projection.setStart(0, 0)

        self.refresh()

    def lButtonDown(self, event):
        self.line1.setStart(event.x, event.y)

    def rButtonDown(self, event):
        global p_line_x
        global p_line_y
        p_line_x = event.x
        p_line_y = event.y

    def mouseMove(self, event):
        if event.state & 0x0100:
            self.line1.setEnd(event.x, event.y)

        if event.state & 0x200:
            theta = math.atan2(event.x - p_line_x, event.y - p_line_y)
            self.projection_line.setVector(p_line_x - math.sin(theta) * 500, p_line_y - math.cos(theta) * 500, math.sin(theta) * 2000, math.cos(theta) * 2000)

    def refresh(self):
        self.updateLine(self.projection_line)
        self.updateLine(self.line1)
        self.line1_projection.setPoints(*App.projectPoint(self.line1.x, self.line1.y, self.projection_line), *App.projectPoint(self.line1.x + self.line1.dx, self.line1.y + self.line1.dy, self.projection_line))
        self.updateLine(self.line1_projection)
        self.line1_1.setPoints(self.line1.x, self.line1.y, self.line1_projection.x, self.line1_projection.y)
        self.updateLine(self.line1_1)
        self.line1_2.setPoints(self.line1.x + self.line1.dx, self.line1.y + self.line1.dy, self.line1_projection.x + self.line1_projection.dx, self.line1_projection.y + self.line1_projection.dy)
        self.updateLine(self.line1_2)

        self.text2.set(f'Line 1: ({int(self.line1.x)},{int(self.line1.y)}) <{int(self.line1.dx)},{int(self.line1.dy)}>')
        self.text3.set(f'Projection: ({int(self.projection_line.x)},{int(self.projection_line.y)}) <{int(self.projection_line.dx)},{int(self.projection_line.dy)}>')

        self.after(15, self.refresh)

    @staticmethod
    def projectPoint(x, y, line):
        if not isinstance(line, Line):
            raise Exception('line argument expected Line object')
        c = ((x - line.x) * line.dx + (y - line.y) * line.dy) / (line.dx ** 2 + line.dy ** 2)
        x = line.dx * c + line.x
        y = line.dy * c + line.y
        return (x, y)

    def updateLine(self, line):
        if not isinstance(line, Line):
            raise Exception('line argument expected Line object')
        self.canvas.coords(line.id, line.x, line.y, line.x + line.dx, line.y + line.dy)

# data model only
class Line(object):
    def __init__(self, root, fill='white', **kwargs):
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.id = root.canvas.create_line(0, 0, 0, 0, fill=fill, **kwargs)

    def setStart(self, x, y):
        self.x = x
        self.y = y

    def setEnd(self, x, y):
        self.dx = x - self.x
        self.dy = y - self.y

    def setVector(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def setPoints(self, x, y, x2, y2):
        self.setStart(x, y)
        self.setEnd(x2, y2)


if __name__ == '__main__':
    root = App()
    root.mainloop()
