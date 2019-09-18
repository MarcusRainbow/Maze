from typing import List
from RatInterface import Rat
from SimpleRats import AlwaysLeftRat, RandomRat

# A simple maze is a vector of vectors of edges. It supports one
# rat at a time. It has one start and one end. WLOG, the start is
# always the first element and the end is one after the last. There is no
# concept of compass directions in this maze, and there is no
# policing to prevent crossing paths.
class SimpleMaze:
    # Initialise with a set of edges. If fill_back_steps is true, we
    # generate backward edges to make it an undirected graph.
    def __init__(self, edges: List[List[int]], fill_back_steps: bool):

        # validate and optionally fill back steps
        end = len(edges)
        if end < 1:
            raise Exception("Must be at least one node")

        has_end = False
        edge_from = 0
        for node in edges:
            if len(set(node)) != len(node):
                raise Exception("Must not have duplicate edges")
            for edge_to in node:
                if edge_to == end:
                    has_end = True  # OK to have multiple routes to end
                elif edge_to > end:
                    raise Exception("Edge out of range")
                elif edge_to == edge_from:
                    raise Exception("Not allowed to have edges to self")
                elif fill_back_steps:
                    # make sure we have a return edge matching this
                    ensure_edge(edges, edge_to, edge_from)
            
            # next node
            edge_from = edge_from + 1

        # We validate that at least one node has an edge leading to the
        # exit. However, we do not currently check that there is a clear
        # path to any such node.
        if not has_end:
            raise Exception("No edge to the end node")

        self.all_edges = edges

    def __str__(self):
        return "SimpleMaze(%s)" % self.all_edges

    def maze(self) -> List[List[int]]:
        return self.all_edges

    # Tries to solve the maze. Returns the number of iterations used.
    # If it exceeds max_iterations, returns max_iterations + 1. If it
    # fails for any other reason, returns 0.
    def solve(self, rat: Rat, max_iterations: int) -> bool:
        
        # always start from the beginning
        pos = 0
        iterations = 0

        # set the last_pos such that the back path is the last in the first list
        last_pos = len(self.all_edges[pos]) - 1
        #print("pos=%i last_pos=%i" % (pos, last_pos))

        # keep going until the end
        end = len(self.all_edges)
        while (pos < end) and (iterations <= max_iterations):
            # find the edges from the current node
            edges = self.all_edges[pos]

            # one of these edges should point back to where we came from
            back = edges.index(last_pos)

            # get the rat to choose a direction
            num_edges = len(edges)
            turn = rat.turn(num_edges)
            if turn == 0:
                iterations = iterations + 1
                continue
            elif (turn > num_edges) or (turn < 0):
                return 0    # give up
            
            # going in some direction
            direction = (turn + back) % num_edges
            last_pos = pos
            pos = edges[direction]
            iterations = iterations + 1
            #print("pos=%i last_pos=%i" % (pos, last_pos))

        # hit the end, or failed with an iteration count that is too high
        # (technically we should worry about the case where we hit max
        # iterations with a valid exit, but this is unlikely and does not
        # matter much).
        return iterations            

# Validates that we have an edge (and if necessary inserts one)
def ensure_edge(edges: List[List[int]], edge_from: int, edge_to: int):
    node = edges[edge_from]
    count = node.count(edge_to)
    if count == 1:
        return      # already have this edge. Nothing more to do
    elif count > 1:
        raise Exception("Edges must be unique")

    # We need this edge. Append it (no attempt to avoid crossing paths)
    node.append(edge_to)

def test_fill_back_steps():
    maze = SimpleMaze([[1, 3], [2], [3, 0]], True)
    print("test_fill_back_steps: %s", maze)
    assert(maze.maze() == [[1, 3, 2], [2, 0], [3, 0, 1]])

def test_left_rat():
    rat = AlwaysLeftRat()
    maze = SimpleMaze([[1, 3], [2], [3, 0]], True)
    MAX_ITER = 10
    iter = maze.solve(rat, MAX_ITER)
    print("test_left_rat solved in %i iterations" % iter)
    assert(iter > 0 and iter <= MAX_ITER)

def test_left_rat_fail():
    rat = AlwaysLeftRat()
    # this maze has a loop in it (0 -> 1 -> 2 -> 0)
    maze = SimpleMaze([[1, 3], [2], [0, 3]], True)
    MAX_ITER = 10
    iter = maze.solve(rat, MAX_ITER)
    print("test_left_rat_fail timed out as desired after %i iterations" % iter)
    assert(iter > MAX_ITER)

def test_random_rat():
    rat = RandomRat()
    maze = SimpleMaze([[1, 3], [2], [3, 0]], True)
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    print("test_random_rat solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_fill_back_steps()
    test_left_rat()
    test_left_rat_fail()
    test_random_rat()
    