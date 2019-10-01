from typing import List, Set, Optional
from random import randrange, shuffle, random
from RatInterface import Rat, MazeInfo
from SimpleRats import AlwaysLeftRat, RandomRat
from Localizer import Localizer, NonLocalLocalizer, OneDimensionalLocalizer, TwoDimensionalOneStepLocalizer
from graphviz import Graph

# A simple maze is a vector of vectors of edges. It supports one
# rat at a time. It has one start and one end. WLOG, the start is
# always the first element and the end is one after the last. There is no
# concept of compass directions in this maze, and there is no
# policing to prevent crossing paths.
class SimpleMaze:
    # Initialise with a set of edges. If fill_back_steps is true, we
    # generate backward edges to make it an undirected graph.
    def __init__(self, edges: List[List[int]], fill_back_steps: bool):
        validate_edges(edges, fill_back_steps)
        self.all_edges = edges

    def __str__(self):
        return "SimpleMaze(%s)" % self.all_edges

    def maze(self) -> List[List[int]]:
        return self.all_edges

    # Tries to solve the maze. Returns the number of iterations used.
    # If it exceeds max_iterations, returns max_iterations + 1. If it
    # fails for any other reason, returns 0.
    def solve(self, rat: Rat, max_iterations: int, info: Optional[MazeInfo] = None) -> bool:
        
        # always start from the beginning
        pos = 0
        iterations = 0

        # set the last_pos such that the back path is the last in the first list
        last_pos = self.all_edges[pos][-1]
        #print("pos=%i last_pos=%i" % (pos, last_pos))

        # keep going until the end
        end = len(self.all_edges)
        while (pos < end) and (iterations <= max_iterations):
            # find the edges from the current node
            edges = self.all_edges[pos]

            # one of these edges should point back to where we came from
            if edges.count(last_pos) != 1:
                print("Problem: no edge from %i to %i" % (pos, last_pos))
            back = edges.index(last_pos)

            # supply maze info for rats that need it. There is only one rat,
            # so supply rat number zero
            num_edges = len(edges)
            if info:
                info.set_pos(pos, back, num_edges, rat)

            # get the rat to choose a direction
            turn = rat.turn(num_edges, info)
            if (turn >= num_edges) or (turn < 0):
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

# validate and optionally fill back steps
def validate_edges(edges: List[List[int]], fill_back_steps: bool):
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

# Validates that we have an edge (and if necessary inserts one)
def ensure_edge(maze: List[List[int]], edge_from: int, edge_to: int):
    node = maze[edge_from]
    count = node.count(edge_to)
    if count == 1:
        return      # already have this edge. Nothing more to do
    elif count > 1:
        raise Exception("Edges must be unique")

    # We need this edge. Append it (no attempt to avoid crossing paths)
    node.append(edge_to)

# Creates a random maze with the specified number of nodes.
def random_maze(allow_loops: float, local: Localizer) -> List[List[int]]:
    # Do NOT write maze = [[]] * node_count as this makes all list elements the same memory!
    node_count = local.node_count()
    maze = [[] for y in range(node_count)]
    
    # Remember all the nodes that connect to the origin. So far, just
    # contains the origin, which is zero by definition.
    accessible = { 0 }

    # First do a random walk until we hit the end. There may be loops,
    # but we don't worry about that. Just make sure there are no duplicate
    # edges. Also, create bidirectional edges as we go.
    edge_from = 0
    while edge_from != node_count:
        edge_to = local.random_step(edge_from, True)
        add_bidirectional_edges(maze, accessible, edge_from, edge_to, allow_loops)
        edge_from = edge_to
    
    # We now have a working maze, but not a very interesting one, in that it
    # just has one random path from start to end. Add some blind alleys and
    # ensure that every node has at least one edge, which somehow connects to
    # the original random walk, hence the start (and the end)
    for i in range(node_count):
        if not (i in accessible):
            # random walk from i until we hit the accessible set
            new_path = { i }
            edge_from = i
            while not (edge_from in accessible):
                edge_to = local.random_step(edge_from, False)   # avoid the exit
                add_bidirectional_edges(maze, new_path, edge_from, edge_to, allow_loops)
                edge_from = edge_to

            # all these nodes are now accessible
            accessible.update(new_path)
    
    # We now have a maze with some blind alleys and all nodes are accessible.
    # Shuffle the edges in each node (we do not want the first edge to always
    # be the one that leads to the exit) and return it.
    for node in maze:
        shuffle(node)
    return maze

# Adds (or at least ensures the existence of) bidirectional edges, and adds
# the end node to a set of accessible nodes. If allow_loops is zero, we prevent
# loops (avoid adding an edge that leads to an accessible node). If it is one,
# we allow them. If between zero and one, we randomly allow them or not.
def add_bidirectional_edges(
    maze: List[List[int]], 
    accessible: Set[int], 
    edge_from: int, 
    edge_to: int,
    allow_loops: float):

    if edge_to != edge_from and allow_edge(allow_loops, edge_to, accessible):
        ensure_edge(maze, edge_from, edge_to)
        if edge_to != len(maze):    # do not need back path from the exit
            ensure_edge(maze, edge_to, edge_from)
        accessible.add(edge_to)

def allow_edge(allow_loops: float, edge_to: int, accessible: Set[int]) -> bool:
    EPSILON = 1e-10
    if allow_loops > 1.0 - EPSILON:
        return True
    elif not (edge_to in accessible):
        return True
    elif allow_loops < EPSILON:
        return False
    elif random() < allow_loops:
        return True
    else:
        return False

# Generate a PDF file showing the maze as an undirected graph. Uses
# GraphViz, which must be installed and on the PATH. Note that
# the resulting graph shows only the nodes and their connections. The
# ordering of edges around each node is determined by GraphViz itself.
# You therefore cannot rely on this rendering to tell you whether to
# turn left or right at each node.
def render_graph(maze: List[List[int]], file_name):
    
    if len(maze) > 26:
        raise Exception("render_graph can only handle up to 26 nodes")

    dot = Graph()
    this = 0
    edges = []
    for node in maze:
        id = str(chr(ord('A') + this))
        if this == 0:
            dot.node(id, "Start (A)")
        else:
            dot.node(id, id)
        for edge in node:
            # avoid duplicating edges by only showing to > from
            if edge > this:
                edge_str = id + str(chr(ord('A') + edge))
                edges.append(edge_str)
        this = this + 1

    # The final node is not in the list, as it exists only as the destination
    # of one or more edge
    id = str(chr(ord('A') + len(maze)))
    dot.node(id, "End (%s)" % id)

    #print(edges)
    dot.edges(edges)
    #print(dot.source)
    dot.render(file_name, view=True)

def test_fill_back_steps():
    maze = SimpleMaze([[1, 3], [2], [3, 0]], True)
    print("test_fill_back_steps: %s" % maze)
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

def test_big_maze():
    rat = RandomRat()
    maze = SimpleMaze([[5, 3], [6], [5, 3, 17, 14, 13, 20], 
        [2, 0, 4, 14, 13, 5, 17, 12], [7, 3], [0, 14, 9, 2, 6, 3],
        [5, 13, 1], [8, 4, 19, 10], [14, 7], [14, 5, 17], [7, 13], 
        [15, 16], [3, 15], [6, 17, 10, 3, 16, 2], [5, 9, 2, 8, 3, 19], 
        [12, 11, 18], [11, 13], [13, 2, 9, 3], [15], [14, 7]], False)
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    print("test_big_maze solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_random_maze():
    maze = SimpleMaze(random_maze(0.5, NonLocalLocalizer(25)), False)
    #print(maze)
    render_graph(maze.maze(), "temp/random_maze")
    rat = RandomRat()
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    print("test_random_maze solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_random_noloop_maze():
    maze = SimpleMaze(random_maze(0.0, NonLocalLocalizer(25)), False)
    #print(maze)
    render_graph(maze.maze(), "temp/random_noloop_maze")
    rat = AlwaysLeftRat()
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    print("test_random_noloop_maze solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_random_1d_maze():
    maze = SimpleMaze(random_maze(0.5, OneDimensionalLocalizer(25, 5)), False)
    #print(maze)
    render_graph(maze.maze(), "temp/random_1d_maze")
    rat = RandomRat()
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    print("test_random_1d_maze solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_random_2d_maze():
    maze = SimpleMaze(random_maze(0.1, TwoDimensionalOneStepLocalizer(25, 5)), False)
    #print(maze)
    render_graph(maze.maze(), "temp/random_2d_maze")
    rat = RandomRat()
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    print("test_random_2d_maze solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_fill_back_steps()
    test_left_rat()
    test_left_rat_fail()
    test_random_rat()
    test_big_maze()
    test_random_maze()
    test_random_noloop_maze()
    test_random_1d_maze()
    test_random_2d_maze()
