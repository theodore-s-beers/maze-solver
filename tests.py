from maze import Maze

test_maze = Maze(50, 50, 12, 12, 40, 40)

count_cells = 0

for i in range(len(test_maze._Maze__cells)):
    for j in range(len(test_maze._Maze__cells[i])):
        count_cells += 1

assert count_cells == 144
print("Correct number of cells!")

top_left_cell = test_maze._Maze__cells[0][0]
assert top_left_cell.has_top_wall is False

bottom_right_cell = test_maze._Maze__cells[11][11]
assert bottom_right_cell.has_bottom_wall is False

print("Correct entry and exit points!")

test_maze._Maze__reset_cells_visited()

for item in test_maze._Maze__cells:
    for cell in item:
        assert cell.visited is False

print("Correctly reset all cells to unvisited!")
