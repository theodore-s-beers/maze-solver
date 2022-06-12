from __future__ import annotations
from tkinter import Tk, Canvas
import time
import random


class _Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class _Line:
    def __init__(self, starting: _Point, ending: _Point):
        self.__starting = starting
        self.__ending = ending

    def draw(self, canv: Canvas, fill_color):
        canv.create_line(
            self.__starting.x,
            self.__starting.y,
            self.__ending.x,
            self.__ending.y,
            fill=fill_color,
            width=2,
        )
        canv.pack()


class Window:
    def __init__(self, width: int, height: int):
        self.__root = Tk()
        self.__root.title("Maze Solver")
        self.__root.protocol("WM_DELETE_WINDOW", self.__close)
        self.__canvas = Canvas(
            self.__root, width=width, height=height, background="white"
        )
        self.__canvas.pack()
        self.__running = False

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def __close(self):
        self.__running = False
        print("Closing window...")

    def draw_line(self, line: _Line, fill_color="black"):
        line.draw(self.__canvas, fill_color)


class _Cell:
    def __init__(self, top_left: _Point, bottom_right: _Point, win: Window = None):
        self.__x1 = top_left.x
        self.__y1 = top_left.y
        self.__x2 = bottom_right.x
        self.__y2 = bottom_right.y
        self.__win = win
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.visited = False

    def draw(self):
        if self.__win is None:
            return

        top_left = _Point(self.__x1, self.__y1)
        bottom_left = _Point(self.__x1, self.__y2)
        top_right = _Point(self.__x2, self.__y1)
        bottom_right = _Point(self.__x2, self.__y2)

        if self.has_left_wall:
            self.__win.draw_line(_Line(top_left, bottom_left))
        else:
            self.__win.draw_line(_Line(top_left, bottom_left), fill_color="white")

        if self.has_right_wall:
            self.__win.draw_line(_Line(top_right, bottom_right))
        else:
            self.__win.draw_line(_Line(top_right, bottom_right), fill_color="white")

        if self.has_top_wall:
            self.__win.draw_line(_Line(top_left, top_right))
        else:
            self.__win.draw_line(_Line(top_left, top_right), fill_color="white")

        if self.has_bottom_wall:
            self.__win.draw_line(_Line(bottom_left, bottom_right))
        else:
            self.__win.draw_line(_Line(bottom_left, bottom_right), fill_color="white")

    def draw_move(self, dest_cell: _Cell, undo=False):
        if self.__win is None:
            return

        origin_center_x = (self.__x1 + self.__x2) // 2
        origin_center_y = (self.__y1 + self.__y2) // 2
        origin_pt = _Point(origin_center_x, origin_center_y)

        dest_center_x = (dest_cell.__x1 + dest_cell.__x2) // 2
        dest_center_y = (dest_cell.__y1 + dest_cell.__y2) // 2
        dest_pt = _Point(dest_center_x, dest_center_y)

        line = _Line(origin_pt, dest_pt)
        fill_color = "white" if undo else "green"
        self.__win.draw_line(line, fill_color)


class Maze:
    def __init__(
        self,
        x1: int,
        y1: int,
        num_rows: int,
        num_cols: int,
        cell_size_x: int,
        cell_size_y: int,
        win: Window = None,
        seed: int = None,
    ):
        self.__x1 = x1
        self.__y1 = y1
        self.__num_rows = num_rows
        self.__num_cols = num_cols
        self.__cell_size_x = cell_size_x
        self.__cell_size_y = cell_size_y
        self.__win = win

        if seed is not None:
            random.seed(seed)

        self.__cells = []
        self.__create_cells()
        self.__break_entrance_and_exit()

        self.__break_walls_r(0, 0)
        self.__reset_cells_visited()

        self.__solve()

    def __create_cells(self):
        for i in range(self.__num_cols):
            col = []
            for j in range(self.__num_rows):
                top_left = _Point(
                    self.__x1 + (i * self.__cell_size_x),
                    self.__y1 + (j * self.__cell_size_y),
                )
                bottom_right = _Point(
                    top_left.x + self.__cell_size_x, top_left.y + self.__cell_size_y
                )
                col.append(_Cell(top_left, bottom_right, self.__win))
            self.__cells.append(col)
        for i in range(self.__num_cols):
            for j in range(self.__num_rows):
                self.__draw_cell(i, j)

    def __draw_cell(self, i: int, j: int):
        if self.__win is None:
            return

        self.__cells[i][j].draw()
        self.__animate()

    def __animate(self):
        if self.__win is None:
            return

        self.__win.redraw()
        time.sleep(0.025)

    def __break_entrance_and_exit(self):
        top_left = self.__cells[0][0]
        bottom_right = self.__cells[self.__num_cols - 1][self.__num_rows - 1]

        top_left.has_top_wall = False
        top_left.draw()

        bottom_right.has_bottom_wall = False
        bottom_right.draw()

    def __break_walls_r(self, i: int, j: int):
        self.__cells[i][j].visited = True

        while True:
            potential_visits = []

            if i > 0:
                left_neighbor = self.__cells[i - 1][j]
                if left_neighbor.visited is False:
                    potential_visits.append((i - 1, j))

            if i < self.__num_cols - 1:
                right_neighbor = self.__cells[i + 1][j]
                if right_neighbor.visited is False:
                    potential_visits.append((i + 1, j))

            if j > 0:
                top_neighbor = self.__cells[i][j - 1]
                if top_neighbor.visited is False:
                    potential_visits.append((i, j - 1))

            if j < self.__num_rows - 1:
                bottom_neighbor = self.__cells[i][j + 1]
                if bottom_neighbor.visited is False:
                    potential_visits.append((i, j + 1))

            if not potential_visits:
                self.__cells[i][j].draw()
                return

            potential_visit_count = len(potential_visits)
            random_choice = random.randint(0, potential_visit_count - 1)

            next_i = potential_visits[random_choice][0]
            next_j = potential_visits[random_choice][1]

            if next_i > i:  # right neighbor chosen
                self.__cells[i][j].has_right_wall = False
                self.__cells[next_i][next_j].has_left_wall = False
            elif next_i < i:  # left neighbor chosen
                self.__cells[i][j].has_left_wall = False
                self.__cells[next_i][next_j].has_right_wall = False
            elif next_j > j:  # bottom neighbor chosen
                self.__cells[i][j].has_bottom_wall = False
                self.__cells[next_i][next_j].has_top_wall = False
            else:  # top neighbor chosen
                self.__cells[i][j].has_top_wall = False
                self.__cells[next_i][next_j].has_bottom_wall = False

            self.__break_walls_r(next_i, next_j)

    def __reset_cells_visited(self):
        for item in self.__cells:
            for cell in item:
                cell.visited = False

    def __solve_r(self, i: int, j: int) -> bool:
        self.__animate()

        current_cell = self.__cells[i][j]
        end_cell = self.__cells[self.__num_cols - 1][self.__num_rows - 1]

        current_cell.visited = True
        if current_cell == end_cell:
            return True

        if i > 0:  # try going left
            left_neighbor = self.__cells[i - 1][j]
            if left_neighbor.visited is False and left_neighbor.has_right_wall is False:
                current_cell.draw_move(left_neighbor)
                if self.__solve_r(i - 1, j) is True:
                    return True
                current_cell.draw_move(left_neighbor, undo=True)

        if i < self.__num_cols - 1:  # try going right
            right_neighbor = self.__cells[i + 1][j]
            if (
                right_neighbor.visited is False
                and right_neighbor.has_left_wall is False
            ):
                current_cell.draw_move(right_neighbor)
                if self.__solve_r(i + 1, j) is True:
                    return True
                current_cell.draw_move(right_neighbor, undo=True)

        if j > 0:  # try going up
            top_neighbor = self.__cells[i][j - 1]
            if top_neighbor.visited is False and top_neighbor.has_bottom_wall is False:
                current_cell.draw_move(top_neighbor)
                if self.__solve_r(i, j - 1) is True:
                    return True
                current_cell.draw_move(top_neighbor, undo=True)

        if j < self.__num_rows - 1:  # try going down
            bottom_neighbor = self.__cells[i][j + 1]
            if (
                bottom_neighbor.visited is False
                and bottom_neighbor.has_top_wall is False
            ):
                current_cell.draw_move(bottom_neighbor)
                if self.__solve_r(i, j + 1) is True:
                    return True
                current_cell.draw_move(bottom_neighbor, undo=True)

        return False

    def __solve(self) -> bool:
        return self.__solve_r(0, 0)
