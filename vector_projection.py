import tkinter as tk
import math
import random


class App(tk.Frame):
    projection_line_start = (0, 0)

    def __init__(self, root):
        super().__init__(master=root)
        root.title('Vector Projection Demo')
        self.root = root

        self.createWidgets()
        self.createBindings()

        self.projection_line = Line(self)
        self.projection_line.setPoints(0, 0, 2000, 2000)
        self.projected_objects = []
        self.projected_objects.append(Polygon(self, 4, 'white'))
        self.projected_objects[-1].center = (350, 100)
        self.projected_objects[-1].radius = 50
        self.projected_objects[-1].angle = math.pi / 4

        self.refresh()

    def createWidgets(self):
        self.canvas = tk.Canvas(master=self, width=500, height=500, background='black', highlightthickness=0)
        sidebar = tk.Frame(master=self)
        label = tk.Label(master=sidebar, text='Left mouse move shape\nRight mouse move projection line\nMouse wheel changes number of sides')
        controls = tk.Frame(master=sidebar)
        buttons = tk.Frame(master=controls)
        add_polygon = tk.Button(master=buttons, text='Add polygon', command=self.addPolygon, wraplength=50)
        remove_polygon = tk.Button(master=buttons, text='Delete polygon', command=self.removePolygon, wraplength=50)
        self.sides_scale = tk.Scale(master=controls, from_=50, to=2, command=self.setNumberOfSides, label='Sides')

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        sidebar.pack(side=tk.LEFT)
        label.pack(pady=(0,100))
        controls.pack()
        buttons.pack(side=tk.LEFT, padx=(0, 50))
        add_polygon.pack(pady=(0,10))
        remove_polygon.pack(pady=(10,0))
        self.sides_scale.pack(side=tk.LEFT)

        self.sides_scale.set(4)

    def setNumberOfSides(self, value):
        if len(self.projected_objects):
            self.projected_objects[-1].setNumberOfSides(value)

    def addPolygon(self):
        if len(self.projected_objects):
            self.canvas.itemconfig(self.projected_objects[-1].id, outline='gray')
        self.projected_objects.append(Polygon(self, self.sides_scale.get(), 'white'))
    
    def removePolygon(self):
        num_objects = len(self.projected_objects)
        if num_objects:
            poly = self.projected_objects[-1]
            self.canvas.delete(poly.id, poly.projection.id, poly.line1.id, poly.line2.id)
            self.projected_objects.pop()
            if num_objects > 1:
                self.canvas.itemconfig(self.projected_objects[-1].id, outline='white')

    def createBindings(self):
        self.canvas.bind('<ButtonPress-1>', self.lButtonDown)
        self.canvas.bind('<ButtonPress-2>', self.rButtonDown)
        self.canvas.bind('<Motion>', self.mouseMove)
        self.canvas.bind("<MouseWheel>", self.mouseWheel)

    def lButtonDown(self, event):
        if len(self.projected_objects):
            self.projected_objects[-1].center = (event.x, event.y)

    def rButtonDown(self, event):
        global projection_line_start
        projection_line_start = (event.x, event.y)

    def mouseMove(self, event):
        if event.state & 0x0100:
            if len(self.projected_objects):
                (x, y) = self.projected_objects[-1].center
                dx = event.x - x
                dy = event.y - y
                self.projected_objects[-1].radius = App.getLineLength(dx, dy)
                self.projected_objects[-1].angle = math.atan2(dx, dy)

        if event.state & 0x200:
            (x, y) = projection_line_start
            theta = math.atan2(event.x - x, event.y - y)
            self.projection_line.setStart(x - math.sin(theta) * 2000, y - math.cos(theta) * 2000)
            self.projection_line.setEnd(x + math.sin(theta) * 2000, y + math.cos(theta) * 2000)

    def mouseWheel(self, event):
        value = self.sides_scale.get()
        value -= event.delta
        value = min(value, self.sides_scale['from'])
        value = max(value, self.sides_scale['to'])
        self.sides_scale.set(value)

    def refresh(self):
    # if self.projection_line.didChange():
        self.update(self.projection_line)
        if len(self.projected_objects):
            # if self.projected_objects[-1].didChange():
            self.update(self.projected_objects[-1])
            self.projectPolygon(self.projected_objects[-1], self.projection_line)
        
        self.after(15, self.refresh)

    @staticmethod
    def projectPoint(x, y, line):
        if not isinstance(line, Line):
            raise Exception('line argument expected Line object')
        dx = line.ex - line.x
        dy = line.ey - line.y
        c = ((x - line.x) * dx + (y - line.y) * dy) / (dx ** 2 + dy ** 2)
        x = dx * c + line.x
        y = dy * c + line.y
        return (x, y)

    @staticmethod
    def getLineLength(x, y, x2=0, y2=0):
        return int(math.sqrt((x - x2) ** 2 + (y - y2) ** 2))

    def update(self, obj):
        if isinstance(obj, Line):
            self.canvas.coords(obj.id, obj.x, obj.y, obj.ex, obj.ey)

        if isinstance(obj, Polygon):
            obj.drawRegularPolygon()
            unpacked_points = []
            for p in obj.points:
                unpacked_points.append(p[0])
                unpacked_points.append(p[1])
            self.canvas.coords(obj.id, *unpacked_points)
            self.update(obj.projection)
            self.update(obj.line1)
            self.update(obj.line2)

    def projectPolygon(self, polygon, line):
        min_normal_point = polygon.points[0]
        min_projected_point = App.projectPoint(*min_normal_point, line)
        min_length = App.getLineLength(*min_projected_point, line.x, line.y)

        max_normal_point = min_normal_point
        max_projected_point = min_projected_point
        max_length = min_length

        for p in polygon.points[1:]:
            projected_point = App.projectPoint(*p, line)
            distance = App.getLineLength(*projected_point, line.x, line.y)
            if distance < min_length:
                min_normal_point = p
                min_projected_point = projected_point
                min_length = distance
            elif distance > max_length:
                max_normal_point = p
                max_projected_point = projected_point
                max_length = distance

        polygon.projection.setPoints(*min_projected_point, *max_projected_point)
        polygon.line1.setPoints(*min_normal_point, *min_projected_point)
        polygon.line2.setPoints(*max_normal_point, *max_projected_point)

# data model only
class Line(object):
    def __init__(self, root, fill='white', **kwargs):
        self.x = 0
        self.y = 0
        self.ex = 0
        self.ey = 0
        # self.changed = 1
        self.id = root.canvas.create_line(0, 0, 0, 0, fill=fill, **kwargs)

    def setStart(self, x, y):
        self.x = x
        self.y = y

    def setEnd(self, x, y):
        self.ex = x
        self.ey = y

    def setPoints(self, x, y, x2, y2):
        self.setStart(x, y)
        self.setEnd(x2, y2)

    # def didChange(self):
    #     if self.changed:
    #         self.changed = 0
    #         return 1
    #     else:
    #         return 0
class Polygon(object):
    def __init__(self, root, sides, outline, **kwargs):
        self.points = [(0, 0) for _ in range(sides)]
        self.sides = sides
        self.center = (0, 0)
        self.radius = 0
        self.angle = 0
        # self.changed = 0
        self.id = root.canvas.create_polygon(*self.points, outline=outline, fill='', **kwargs)
        self.projection = Line(root, 'red', arrow='both')
        self.line1 = Line(root, dash=5)
        self.line2 = Line(root, dash=5)

    # def setAngle(self, value):
    #     self.angle = value
    #     self.changed = 1

    # def didChange(self):
    #     if self.changed:
    #         self.changed = 0
    #         return 1
    #     else:
    #         return 0

    def setNumberOfSides(self, sides):
        self.sides = int(sides)
        if self.sides != len(self.points):
            self.points = []
            self.points = [(0, 0) for _ in range(self.sides)]
        
    def drawRegularPolygon(self):
        (x, y) = self.center
        radius = self.radius
        theta = self.angle
        total_radians = (self.sides - 2) * math.pi
        corner_radians = math.pi - total_radians / self.sides
        for i in range(self.sides):
            px = x + math.sin(theta + corner_radians * i) * radius
            py = y + math.cos(theta + corner_radians * i) * radius
            self.points[i] = (px, py)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    app.pack(fill=tk.BOTH, expand=1)
    root.mainloop()
