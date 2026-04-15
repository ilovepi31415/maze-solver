from tkinter import Tk, BOTH, Canvas
import time, random

class Window():
    def __init__(self, width, height):
        self.__root = Tk(className="Maze Solver")
        self.__root.geometry(f"{width}x{height}")
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

        self.canvas = Canvas(self.__root, width=width, height=height)
        self.canvas.pack()

        self.running = False
    
    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()
    
    def wait_for_close(self):
        self.running = True
        while self.running == True:
            self.redraw()
        
    def close(self):
        self.running = False

    def draw_line(self, line, fill):
        line.draw(fill)

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line():
    def __init__(self, point_1, point_2):
        self.start = point_1
        self.end = point_2

    def draw(self, canvas, fill):
        canvas.create_line(
            self.start.x, self.start.y, self.end.x, self.end.y, fill=fill, width=2
        )

class Cell():
    def __init__(self, window=None):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.__x1 = -1
        self.__x2 = -1
        self.__y1 = -1
        self.__y2 = -1
        self.visited = False
        self.__win = window

    def draw(self, x, y, width, height):
        self.__x1 = x
        self.__y1 = y
        self.__x2 = x + width
        self.__y2 = y + height
        a = Point(self.__x1, self.__y1)
        b = Point(self.__x2, self.__y1)
        c = Point(self.__x1, self.__y2)
        d = Point(self.__x2, self.__y2)
        top = Line(a, b)
        right = Line(b, d)
        left = Line(a, c)
        bottom = Line(c, d)
        if self.__win:
            if self.has_left_wall:
                left.draw(self.__win.canvas, "black" if self.has_left_wall else "#d9d9d9")
            right.draw(self.__win.canvas, "black" if self.has_right_wall else "#d9d9d9")
            top.draw(self.__win.canvas, "black" if self.has_top_wall else "#d9d9d9")
            bottom.draw(self.__win.canvas, "black" if self.has_bottom_wall else "#d9d9d9")

    def draw_move(self, to_cell: "Cell", undo=False):
        center_x = (self.__x1 + self.__x2) / 2
        center_y = (self.__y1 + self.__y2) / 2
        center_start = Point(center_x, center_y)

        other_x = (to_cell.__x1 + to_cell.__x2) / 2
        other_y = (to_cell.__y1 + to_cell.__y2) / 2
        center_end = Point(other_x, other_y)

        color = "red" if undo else "blue"
        connection = Line(center_start, center_end)
        if (self.__win):
            connection.draw(self.__win.canvas, color)

class Maze():
    def __init__(self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win=None, seed=None):
        if not seed:
            random.seed(seed)
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win
        self.__cells:list[list["Cell"]] = []
        self.__create_cells()
        # Draw cell grid
        for i in range(len(self.__cells)):
            for j in range(len(self.__cells[0])):
                self.__draw_cell(i, j)
                self.__animate()
        self.__break_entrance_and_exit()
        self.__break_walls_r(0, 0)
        self.__reset_cells_visited()
        self.__solve_r(0, 0)

    def __create_cells(self):
        for i in range(self.num_cols):
            row = []
            for j in range(self.num_rows):
                c = Cell(self.win)
                row.append(c)
            self.__cells.append(row)
    
    def __draw_cell(self, i, j):
        x = self.x1 + (self.cell_size_x * i)
        y = self.y1 + (self.cell_size_y * j)
        self.__cells[i][j].draw(x, y, self.cell_size_x, self.cell_size_y)

    def __animate(self):
        if self.win:
            self.win.redraw()
            time.sleep(.001)

    def __break_entrance_and_exit(self):
        self.__cells[0][0].has_top_wall = False
        self.__draw_cell(0, 0)
        self.__cells[-1][-1].has_bottom_wall = False
        self.__draw_cell(self.num_cols - 1, self.num_rows - 1)
    
    def __break_walls_r(self, i, j):
        while True:
            options = []
            left, right, up, down = None, None, None, None
            curr: "Cell" = self.__cells[i][j]
            curr.visited = True
            if i > 0:
                left = self.__cells[i-1][j]
            if i < self.num_cols - 1:
                right = self.__cells[i+1][j]
            if j > 0:
                up = self.__cells[i][j-1]
            if j < self.num_rows - 1:
                down = self.__cells[i][j+1]
            if i > 0 and not left.visited:
                options.append(left)
            if i < self.num_cols - 1 and not right.visited:
                options.append(right)
            if j > 0 and not up.visited:
                options.append(up)
            if j < self.num_rows - 1 and not down.visited:
                options.append(down)
            if len(options) == 0:
                return
            self.__animate()
            next: "Cell" = random.choice(options)
            if next == left:
                curr.has_left_wall = False
                next.has_right_wall = False
                self.__draw_cell(i, j)
                self.__draw_cell(i-1, j)
                self.__break_walls_r(i-1, j)
            if next == right:
                curr.has_right_wall = False
                next.has_left_wall = False
                self.__draw_cell(i, j)
                self.__draw_cell(i+1, j)
                self.__break_walls_r(i+1, j)
            if next == up:
                curr.has_top_wall = False
                next.has_bottom_wall = False
                self.__draw_cell(i, j)
                self.__draw_cell(i, j-1)
                self.__break_walls_r(i, j-1)
            if next == down:
                curr.has_bottom_wall = False
                next.has_top_wall = False
                self.__draw_cell(i, j)
                self.__draw_cell(i, j+1)
                self.__break_walls_r(i, j+1)

    def __reset_cells_visited(self):
        for i in range(len(self.__cells)):
            for j in range(len(self.__cells[0])):
                self.__cells[i][j].visited = False
    
    def __solve_r(self, i, j):
        self.__animate()
        if i == self.num_cols - 1 and j == self.num_rows - 1:
            return True
        curr: "Cell" = self.__cells[i][j]
        curr.visited = True
        if j < self.num_rows-1 and not curr.has_bottom_wall and not self.__cells[i][j+1].visited:
            curr.draw_move(self.__cells[i][j+1])
            if self.__solve_r(i, j+1):
                return True
            curr.draw_move(self.__cells[i][j+1], True)
        if i < self.num_cols-1 and not curr.has_right_wall and not self.__cells[i+1][j].visited:
            curr.draw_move(self.__cells[i+1][j])
            if self.__solve_r(i+1, j):
                return True
            curr.draw_move(self.__cells[i+1][j], True)
        if i > 0 and not curr.has_left_wall and not self.__cells[i-1][j].visited:
            curr.draw_move(self.__cells[i-1][j])
            if self.__solve_r(i-1, j):
                return True
            curr.draw_move(self.__cells[i-1][j], True)
        if j > 0 and not curr.has_top_wall and not self.__cells[i][j-1].visited:
            curr.draw_move(self.__cells[i][j-1])
            if self.__solve_r(i, j-1):
                return True
            curr.draw_move(self.__cells[i][j-1], True)
        return False

def main():
    win = Window(800, 600)

    maze = Maze(50, 50, 25, 35, 20, 20, win)

    win.wait_for_close()

if __name__ == "__main__":
    main()
