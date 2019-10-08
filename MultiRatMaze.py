from typing import List, Set, Optional, Tuple
from random import randrange, shuffle, random
from RatInterface import Rat, MazeInfo
from SimpleRats import AlwaysLeftRat, RandomRat
from SimpleMaze import random_maze, render_graph, validate_edges
from Localizer import Localizer, NonLocalLocalizer, OneDimensionalLocalizer, TwoDimensionalOneStepLocalizer
from graphviz import Graph

# A multi-rat maze supports more than one rat, moving at different
# speeds. The speed of each rat is defined by an integer, stating how
# often the rat moves.
class MultiRatMaze:
    # Initialise with a set of edges. If fill_back_steps is true, we
    # generate backward edges to make it an undirected graph.
    def __init__(self, edges: List[List[int]], fill_back_steps: bool):
        validate_edges(edges, fill_back_steps)
        self.all_edges = edges

    def __str__(self):
        return "MultiRatMaze(%s)" % self.all_edges

    def maze(self) -> List[List[int]]:
        return self.all_edges

    # Tries to solve the maze. Returns the number of iterations used.
    # If it exceeds max_iterations, returns max_iterations + 1. The rats
    # parameter is a list of rats and their associated speeds (one being fastest,
    # two meaning wait every other turn etc.) Either wait for all rats,
    # or exit as soon as the fastest rat has quit.
    def solve(
        self, 
        rats: List[Tuple[Rat, int]], 
        max_iterations: int,
        wait_for_all: bool = False,
        info: Optional[MazeInfo] = None) -> bool:

        rat_count = len(rats)
        if rat_count == 0:
            raise Exception("No rats supplied")

        # Always start all rats from the beginning (may want to relax this
        # constraint)
        pos = [0] * rat_count
        iterations = 0

        # set the last_pos such that the back path is the last in the first list
        last = self.all_edges[0][-1]
        last_pos = [last] * rat_count
        #print("pos=%i last_pos=%i" % (pos, last_pos))

        # keep going until the either all rats have finished or just one (or we ran
        # out of iterations)
        end = len(self.all_edges)
        while not has_finished(pos, end, iterations, max_iterations, wait_for_all):
            iterations = iterations + 1

            # First update the info for any rats that are newly in this location
            if info:
                for (i, (rat, speed)) in enumerate(rats):
                    if (iterations - 1) % speed == 0:
                        # find the edges from the current node
                        edges = self.all_edges[pos[i]]

                        # one of these edges should point back to where we came from
                        if edges.count(last_pos[i]) != 1:
                            print("Problem: no edge from %i to %i" % (pos[i], last_pos[i]))
                        back = edges.index(last_pos[i])
                        num_edges = len(edges)

                        # update the info
                        info.set_pos(pos[i], back, num_edges, rat)

            # Next, for any rats that are not skipping this turn, make the turn
            for (i, (rat, speed)) in enumerate(rats):
                if iterations % speed != 0:
                    continue    # skip a turn for this rat

                # get the rat to choose a direction
                edges = self.all_edges[pos[i]]
                back = edges.index(last_pos[i])
                num_edges = len(edges)
                turn = rat.turn(num_edges, info)
                if (turn >= num_edges) or (turn < 0):
                    raise Exception("Rat turn out of range")
                
                # convert it to an absolute direction and make the move
                direction = (turn + back) % num_edges
                last_pos[i] = pos[i]
                pos[i] = edges[direction]
                #print("pos=%i last_pos=%i" % (pos, last_pos))

        # hit the end, or failed with an iteration count that is too high
        # (technically we should worry about the case where we hit max
        # iterations with a valid exit, but this is unlikely and does not
        # matter much).
        return iterations            

def has_finished(pos: List[int], end: int, iterations: int, max_iterations: int, wait_for_all: bool) -> bool:
    if iterations > max_iterations:
        return True
    
    if wait_for_all:
        return all(p == end for p in pos)
    else:
        return end in pos

def test_multiple_left_rats():
    rat = AlwaysLeftRat()   # content-less rat, so only need one
    rats = [(rat, 2), (rat, 3)]
    maze = MultiRatMaze([[1, 3], [2], [3, 0]], True)
    MAX_ITER = 10
    iter = maze.solve(rats, MAX_ITER)
    print("test_left_multi_rats solved in %i iterations" % iter)
    assert(iter > 0 and iter <= MAX_ITER)

def test_big_multimaze():
    rat = RandomRat()   # content-less rat, so only need one
    rats = [(rat, 2), (rat, 3)]
    maze = MultiRatMaze([[5, 3], [6], [5, 3, 17, 14, 13, 20], 
        [2, 0, 4, 14, 13, 5, 17, 12], [7, 3], [0, 14, 9, 2, 6, 3],
        [5, 13, 1], [8, 4, 19, 10], [14, 7], [14, 5, 17], [7, 13], 
        [15, 16], [3, 15], [6, 17, 10, 3, 16, 2], [5, 9, 2, 8, 3, 19], 
        [12, 11, 18], [11, 13], [13, 2, 9, 3], [15], [14, 7]], False)
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER)
    print("test_big_maze solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_random_1d_multimaze():
    maze = MultiRatMaze(random_maze(0.5, OneDimensionalLocalizer(25, 5)), False)
    render_graph(maze.maze(), "temp/random_1d_multimaze")
    rat = RandomRat()
    rats = [(rat, 2), (rat, 3)]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER)
    print("test_random_1d_multimaze solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_multiple_left_rats()
    test_big_multimaze()
    test_random_1d_multimaze()
