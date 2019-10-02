from random import randrange, seed
from typing import List, Set
from copy import deepcopy
from RatInterface import Rat, MazeInfo
from SimpleMaze import SimpleMaze, random_maze, render_graph
from Localizer import OneDimensionalLocalizer

UNKNOWN = -1     # node that we have not yet visited

class MemoryRat(Rat):

    def __init__(self):
        # same data structure as a maze, except that unknown edges
        # are labelled as -1
        self.picture : List[List[int]] = []
        self.dead_ends : Set[int] = set()
        self.prev_node = UNKNOWN
        self.prev_edge = UNKNOWN
        self.next_node = UNKNOWN

    def final_picture(self) -> List[List[int]]:
        # add the final edge, which we know takes us to the exit
        result = deepcopy(self.picture)
        end = len(result)
        if self.prev_node >= 0:
            result[self.prev_node][self.prev_edge] = end
        return result

    # The maze asks which way we want to turn. We remember a picture
    # of the maze as we go. This may not be accurate, because loops
    # appear as repeats (we cannot tell the difference). However, it
    # should help us to find the exit.
    def turn(self, directions: int, _: MazeInfo) -> int:
        assert(directions > 0)

        #print("turn: %i directions prev=(%i %i) next=%i picture=%s" 
        #    % (directions, self.prev_node, self.prev_edge, self.next_node, self.picture))
        
        # if this is a node we've not visited yet, then add it to the picture
        if self.next_node == UNKNOWN:

            # patch up previous node, if any
            this_node = len(self.picture)
            if self.prev_node >= 0:
                self.picture[self.prev_node][self.prev_edge] = this_node

            # add new node to picture
            self.picture.append([UNKNOWN] * directions)
            self.picture[this_node][0] = self.prev_node

            # if there is only one direction, step in it and mark this as a dead-end
            if directions == 1:
                self.dead_ends.add(this_node)
                self.next_node = self.prev_node
                self.prev_node = this_node
                self.prev_edge = 0
                return 0
 
            # step in a random direction, but not backwards unless start
            at_start = self.prev_node == UNKNOWN
            include_back = 0 if at_start else 1
            self.prev_node = this_node
            self.prev_edge = randrange(include_back, directions)
            self.next_node = UNKNOWN
            #print("  new node: stepping to unknown (%i)" % self.prev_edge)
            return self.prev_edge

        # This is a node we've already visited. Check we are where we think
        # we are.
        current_node = self.picture[self.next_node]
        if directions != len(current_node):
            raise Exception("We are lost: directions=%i current_node=%s picture=%s" % (directions, current_node, self.picture))

        # Find where we came from. (We assume that the maze has at most one
        # edge between any two nodes.)
        try:
            back = current_node.index(self.prev_node)
        except:
            raise Exception("Cannot find where we came from: prev_node=%i next_node=%i picture=%s" % (self.prev_node, self.next_node, self.picture))

        # If there is only one exit that is not a dead-end, mark this
        # as a dead-end
        valid_exits = [i for i, x in enumerate(current_node) if x not in self.dead_ends]
        valid_exit_count = len(valid_exits)
        assert(valid_exit_count > 0)
        if valid_exit_count == 1:
            self.dead_ends.add(self.next_node)

        # Find a valid exit at random and go that way
        # (maybe consider not going backwards, or prioritising unknowns?)
        choice = randrange(0, valid_exit_count)
        valid_exit = valid_exits[choice]

        # Note that we need to return the direction
        # in the callers frame of reference, not ours
        self.prev_node = self.next_node
        self.prev_edge = valid_exit
        self.next_node = current_node[valid_exit]
        turn = (valid_exit - back + directions) % directions
        #print("  old node: stepping to %i (%i) back=%i" % (self.next_node, turn, back))
        return turn

def test_memory_rat_no_loops():
    maze = SimpleMaze(random_maze(0.0, OneDimensionalLocalizer(25, 5)), False)
    #print(maze)
    #seed(1000)
    #maze = SimpleMaze([[1], [0, 4, 3], [3], [5, 1, 2], [7, 1], [3, 6], [5], [10, 4, 9], [9], [7, 8]], False)
    rat = MemoryRat()
    MAX_ITER = 100
    iter = maze.solve(rat, MAX_ITER)
    render_graph(maze.maze(), "temp/memory_maze")
    #print("final: %s" % rat.final_picture())
    render_graph(rat.final_picture(), "temp/memory_picture")
    print("test_memory_rat_no_loops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_memory_rat_loops():
    maze = SimpleMaze(random_maze(0.5, OneDimensionalLocalizer(25, 5)), False)
    rat = MemoryRat()
    MAX_ITER = 100
    iter = maze.solve(rat, MAX_ITER)
    render_graph(maze.maze(), "temp/memory_maze_loops")
    render_graph(rat.final_picture(), "temp/memory_picture_loops")
    print("test_memory_rat_loops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_memory_rat_no_loops()
    test_memory_rat_loops()
