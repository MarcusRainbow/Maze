from random import randrange, seed
from typing import List
from RatInterface import Rat, MazeInfo
from SimpleMaze import SimpleMaze, random_maze, render_graph
from Localizer import OneDimensionalLocalizer

UNKNOWN = -1     # node that we have not yet visited
DEAD_END = -2    # node that is a dead end
PENDING_DELETE = -3  # placeholder for the node that is being deleted (there can be only one) 

class MemoryRat(Rat):

    def __init__(self):
        # same data structure as a maze, except that unknown edges
        # are labelled as -1, and dead-ends are labelled as -2
        self.picture : List[List[int]] = []
        self.prev_node = UNKNOWN
        self.prev_edge = UNKNOWN
        self.next_node = UNKNOWN

    # The maze asks which way we want to turn. We remember a picture
    # of the maze as we go. This may not be accurate, because loops
    # appear as repeats (we cannot tell the difference). However, it
    # should help us to find the exit.
    def turn(self, directions: int, _: MazeInfo) -> int:
        assert(directions > 0)

        #print("turn: %i directions prev=(%i %i) next=%i picture=%s" 
        #    % (directions, self.prev_node, self.prev_edge, self.next_node, self.picture))
        
        # if this is a node we've not visited yet, then add it to
        # the picture, unless it is a dead-end
        if self.next_node == UNKNOWN:
            at_start = self.prev_node == UNKNOWN

            # trim dead-ends as we go
            if directions == 1:
                self.next_node = self.prev_node
                self.prev_edge = 0

                # If we are walking from a real node, set the back track to 
                # PENDING_DELETE so it is fixed up when we return to it. If
                # we are walking from the start or a node that is already
                # marked as a DEAD_END, mark it as DEAD_END straight away.
                if self.prev_node >= 0:
                    self.picture[self.prev_node][self.prev_edge] = PENDING_DELETE
                    self.prev_node = PENDING_DELETE
                else:
                    self.prev_node = DEAD_END
                #print("  dead end: returning to %i (0)" % self.prev_node)
                return 0

            # patch up previous node, if any
            this_node = len(self.picture)
            if self.prev_node >= 0:
                self.picture[self.prev_node][self.prev_edge] = this_node

            # add new node to picture
            self.picture.append([UNKNOWN] * directions)
            self.picture[this_node][0] = self.prev_node

            # step in a random direction, but not backwards
            include_back = 0 if at_start else 1
            self.stepping_into_the_unknown = True
            self.prev_node = this_node
            self.prev_edge = randrange(include_back, directions)
            self.next_node = UNKNOWN
            #print("  new node: stepping to unknown (%i)" % self.prev_edge)
            return self.prev_edge

        # This is a node we've already visited. Check we are where we think
        # we are.
        try:
            current_node = self.picture[self.next_node]
        except:
            raise Exception("self.next_node=%i len(self.picture)=%i" % (self.next_node, len(self.picture)))
        if directions != len(current_node):
            raise Exception("We are lost: directions=%i current_node=%s picture=%s" % (directions, current_node, self.picture))

        # Find where we came from. (We assume that the maze has at most one
        # edge between any two nodes.)
        try:
            back = current_node.index(self.prev_node)
        except:
            raise Exception("not found: prev_node=%i next_node=%i picture=%s" % (self.prev_node, self.next_node, self.picture))

        # If there is a node that is pending deletion, mark it as a dead end
        pending_delete = current_node.count(PENDING_DELETE)
        assert(pending_delete == 0 or pending_delete == 1)
        if pending_delete == 1:
            to_delete = current_node.index(PENDING_DELETE)
            current_node[to_delete] = DEAD_END

        # If there are is only one exit that is not a dead-end, mark this
        # as a dead-end, and head in the only available direction
        valid_exits = directions - current_node.count(DEAD_END)
        assert(valid_exits > 0)
        if valid_exits == 1:
            self.prev_node = PENDING_DELETE
            self.prev_edge = 0
            i = next((j for j, x in enumerate(current_node) if x != DEAD_END))
            this_node = self.next_node
            self.next_node = current_node[i]
            self.mark_dead_end(this_node, self.next_node)
            turn = (i - back + directions) % directions
            #print("  old node is dead end: stepping to %i (%i)" % (self.next_node, turn))
            return turn

        # Not a dead-end, so find a valid exit at random and go that way
        # (maybe consider not going backwards, or prioritising unknowns?)
        choice = randrange(0, valid_exits)
        for i in range(directions):
            if current_node[i] != DEAD_END:
                if choice == 0:
                    # found it. Note that we need to return the direction
                    # in the callers frame of reference, not ours
                    self.prev_node = self.next_node
                    self.prev_edge = i
                    self.next_node = current_node[i]
                    turn = (i - back + directions) % directions
                    #print("  old node: stepping to %i (%i) back=%i" % (self.next_node, turn, back))
                    return turn
                choice = choice - 1
        
        assert(False)   # should not get here

    # If a node has only one exit that is not a dead-end, we can mark
    # that node itself as dead. Remove all its exits and mark
    # anything that points to it as dead. (Ideally, we'd remove it from
    # the list, but that means shuffling everything.)
    def mark_dead_end(self, node: int, next: int):

        #print("mark dead end: node=%i next=%i" % (node, next))
        #print("  before: %s" % self.picture)
        # every edge in the maze is bidirectional, so we can find nodes that
        # refer to this one by looking through this node's edges.
        current_node = self.picture[node]
        for edge in current_node:
            if edge >= 0:
                other = self.picture[edge]
                if node in other:
                    i = other.index(node)
                    # mark the one node we are going to next as PENDING_DELETE
                    # rather than DEAD_END, so we can find the passage we emerge
                    # from. We then fix it to DEAD_END
                    other[i] = PENDING_DELETE if edge == next else DEAD_END
            
        # finally, kill off all edges in this node
        self.picture[node] = []
        #print("  after:  %s" % self.picture)

def test_memory_rat():
    maze = SimpleMaze(random_maze(0.0, OneDimensionalLocalizer(10, 3)), False)
    print(maze)
    #seed(1000)
    #maze = SimpleMaze([[1], [0, 4, 3], [3], [5, 1, 2], [7, 1], [3, 6], [5], [10, 4, 9], [9], [7, 8]], False)
    rat = MemoryRat()
    MAX_ITER = 100
    iter = maze.solve(rat, MAX_ITER)
    render_graph(maze.maze(), "temp/memory_maze")
    print("test_memory_rat solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_memory_rat()
