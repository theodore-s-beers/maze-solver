from lib import Window, Maze


def main():
    win = Window(800, 600)

    _ = Maze(50, 50, 12, 12, 40, 40, win)

    win.wait_for_close()


if __name__ == "__main__":
    main()
