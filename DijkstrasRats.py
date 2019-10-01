import random
from typing import List
from RatInterface import Rat, MazeInfo
from SimpleMaze import SimpleMaze, random_maze, render_graph
from Localizer import OneDimensionalLocalizer

class DijkstrasMazeInfo(MazeInfo):
    def __init__(self, maze: List[List[int]]):
        self.maze = maze
        self.position = -1
        self.direction = -1

    def set_pos(self, pos: int, back: int, _directions: int, _rat: Rat):
        self.position = pos
        self.back = back

    # Returns the current position in the maze
    def pos(self) -> int:
        assert self.position >= 0
        return self.position

    # Returns what would be the next position in the maze
    # if we were to set off in the direction specified
    # by turn (1..num_edges)
    def peek(self, turn: int) -> int:
        assert self.position >= 0
        assert self.back >= 0
        assert turn > 0
 
        node = self.maze[self.position]
        num_edges = len(node)
        assert turn <= num_edges
        direction = (turn + self.back) % num_edges

        return node[direction]

class DijkstrasRat(Rat):

    def __init__(self, end: int):
        self.end = end
        # Initially all nodes are unvisited. We set the distance to zero
        # for the starting node, and omit all the others, to say that
        # they are unvisited.
        self.distance = {0: 0}
        self.visited = set()

    # The maze asks which way we want to turn. We use Dijkstra's
    # algorithm to determine which way to go, where the
    # heuristic distance is the number of nodes minus the pos.
    def turn(self, directions: int, info: MazeInfo) -> int:
        pos = info.pos()
        distance = self.distance[pos]

        # update any unvisited nodes with the distance from this node (STEP_SIZE)
        STEP_SIZE = 1
        min_dir = 0
        min_distance = 0
        unvisited = 0
        for dir in range(1, directions + 1):
            node = info.peek(dir)
            if node not in self.visited:
                unvisited = unvisited + 1
                edge_distance = self.update_distance(node, distance + STEP_SIZE)
                if min_dir == 0 or edge_distance < min_distance:
                    min_distance = edge_distance
                    min_dir = dir

        # If all nodes have been visited, this is a problem
        if unvisited == 0:
            raise Exception("Hit a problem. We have visited all nodes and have nowhere to go")

        # If all nodes but one have been visited (presumably the node we came from,
        # as that clearly must have been open), mark this node as visited and return
        elif unvisited == 1:
            self.visited.add(pos)

        # show where we are and how we are progressing
        A = ord('A')
        print("pos=%s directions=%i unvisited=%i next=%s next_distance=%i" %
            (chr(pos + A), directions, unvisited, chr(min_dir + A), min_distance))
        visited_as_str = { chr(v + A) for v in self.visited }
        distance_as_str = { chr(n + A): d for (n, d) in self.distance.items() }
        print("  visited: %s" % visited_as_str)
        print("  distance: %s" % distance_as_str)

        # Head in the direction of the shortest unvisited node
        assert min_dir > 0
        return min_dir        

    def update_distance(self, node: int, distance: int) -> int:
        if node not in self.distance or self.distance[node] > distance:
            self.distance[node] = distance
        
        return self.distance[node]

    # Returns the distance from start to end (-1 if we never got there)
    def distance_to_end(self) -> int:
        if self.end not in self.distance:
            return -1
        else:
            return self.distance[self.end]

def test_dijkstras_rat():
    SIZE = 6
    maze = SimpleMaze(random_maze(0.5, OneDimensionalLocalizer(SIZE, 3)), False)
    #print(maze)
    render_graph(maze.maze(), "temp/dijkstras_maze")
    rat = DijkstrasRat(SIZE)
    info = DijkstrasMazeInfo(maze.maze())
    MAX_ITER = 30
    iter = maze.solve(rat, MAX_ITER, info)
    print("test_dijkstras_rat solved in %i iterations" % iter)
    print("  distance from start to end is %i" % rat.distance_to_end())
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_dijkstras_rat()
