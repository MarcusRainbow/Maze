import random
from typing import List, Dict
from RatInterface import Rat, MazeInfo
from SimpleMaze import SimpleMaze, random_maze, render_graph
from Localizer import OneDimensionalLocalizer

class TremauxMazeInfo(MazeInfo):
    """
    Algorithm developed by the 19th century French engineer, Charles
    Tremaux. It solves any maze quite efficiently, including those with
    loops.

    Whenever you enter or leave a tunnel, mark a dot at the end of the
    tunnel. Thus if you enter a dead-end and immediately leave it, you
    mark two dots. If you enter a chamber and all exits have two dots,
    you know the maze is insoluble. If you enter a chamber with some
    exits that have no dots, pick one and walk along it, otherwise
    pick an exit that has one dot and walk along that.

    This only works if you can make marks in the maze, or equivalently
    if the tunnels are identifiable, and you can remember where you have
    been.
    """
    def __init__(self):
        self.edge_marks : Dict[(int, int): int] = {}
        self.position = -1
        self.back = -1
        self.started = False

    def set_pos(self, pos: int, back: int, _directions: int, _rat: Rat):
        self.position = pos
        self.back = back

    def invalidate_pos(self, _rat: Rat):
        pass

    def choose_turn(self, directions: int) -> int:
        """
        Picks which way to turn. Takes the number of
        possible directions (including backwards) and
        returns one of them. Note that the directions
        are relative to the way we came into the node,
        with 0 meaning go backwards, 1 meaning turn left
        etc.
        """
        assert self.position >= 0
        assert self.back >= 0

        #print("pos=%i back=%i" % (self.position, self.back))
        #print("  marks before turn: %s" % self.edge_marks)

        # mark the end of the passage we just emerged from
        if self.started:
            self.add_mark(self.back)
        else:
            self.started = True

        # look for the direction with fewest marks
        min_mark = 2
        min_dir = -1
        for i in range(directions):
            # convert to an absolute direction
            direction = (i + self.back) % directions
            mark = self.get_mark(direction)
            if mark < min_mark:
                min_mark = mark
                min_dir = i
        
        # if there are no valid directions, give up
        if min_mark == 2:
            raise Exception("No valid directions to try")
        
        # otherwise go the best way possible, first adding
        # a mark to that passage
        self.add_mark((min_dir + self.back) % directions)

        #print("  marks after turn: %s" % self.edge_marks)

        return min_dir

    def add_mark(self, direction: int):
        edge = (self.position, direction)
        if edge in self.edge_marks:
            self.edge_marks[edge] = self.edge_marks[edge] + 1
            assert self.edge_marks[edge] <= 2
        else:
            self.edge_marks[edge] = 1
    
    def get_mark(self, direction: int) -> int:
        edge = (self.position, direction)
        if edge in self.edge_marks:
            return self.edge_marks[edge]
        else:
            return 0

class TremauxRat(Rat):

    def turn(self, directions: int, info: MazeInfo) -> int:
        """
        The maze asks which way we want to turn. We use Tremaux's
        algorithm to determine which way to go.
        """
        return info.choose_turn(directions)

def test_tremaux_rat():
    SIZE = 25
    maze = SimpleMaze(random_maze(0.5, OneDimensionalLocalizer(SIZE, 3)), False)
    #print(maze)
    render_graph(maze.maze(), "temp/tremaux_maze")
    rat = TremauxRat()
    info = TremauxMazeInfo()
    MAX_ITER = 100
    iter = maze.solve(rat, MAX_ITER, info)
    print("test_tremaux_rat solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_tremaux_rat()
