from random import randrange, seed
from typing import List, Set, Dict
from copy import deepcopy
from RatInterface import Rat, MazeInfo
from SimpleMaze import SimpleMaze, random_maze, render_graph, are_equal_mazes
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
        turn = (valid_exit - back) % directions
        #print("  old node: stepping to %i (%i) back=%i" % (self.next_node, turn, back))
        return turn

    # Merges the memories of two rats. Memories are merged with the
    # assumption that both rats started in the same place, and are now in the same
    # place. Neither rat has yet been asked to turn, which means that its
    # current state is that its position is self.next_node (which may be UNKNOWN)
    def merge(self, other: Rat, directions: int, tunnel: int):

        # Nothing to do if we already agree.
        if self.picture == other.picture:
            return

        print("merge(%i, %i): self=%i other=%i" % (directions, tunnel, self.next_node, other.next_node))
        print(self.picture)
        print(other.picture)

        # the mazes should be the same, as far as we can see (parts may be unknown
        # in either or both)
        my_old_picture = deepcopy(self.picture)
        other_old_picture = deepcopy(other.picture)
        assert(are_equal_mazes(my_old_picture, other_old_picture))

        # For both our picture and the other picture, ensure that the
        # next node is represented.
        self.ensure_next_exists(directions)
        other.ensure_next_exists(directions)

        #print("after ensure_next: self=%i other=%i" % (self.next_node, other.next_node))
        #print(self.picture)
        #print(other.picture)

        # Walk both pictures from the start, trying to find mappings
        # between nodes in the two pictures. Then do the same from the end.
        node_mapping: Dict[int, int] = {}
        #print("add node mappings from the start (my next = %i, other = %i)" % (self.next_node, other.next_node))
        self.add_node_mapping(other, 0, 0, 0, node_mapping)
        #print("add node mappings from the end (my next = %i, other = %i)" % (self.next_node, other.next_node))
        self.add_node_mapping(other, self.next_node, other.next_node, tunnel, node_mapping)

        #print("node mapping: %s" % node_mapping)

        # Walk both pictures from the start, adding nodes and edges that
        # are known to other into self. Then do the same from the end.
        traversed: Set[int] = set()
        self.add_missing(other, 0, 0, 0, node_mapping, traversed)

        #print("After adding missing to self: %s" % self.picture)

        self.add_missing(other, self.next_node, other.next_node, tunnel, node_mapping, traversed)

        # We have modified our own picture, given the information from the other Rat.
        # Now do the same thing in reverse.
        rev_mapping = { v: k for (k, v) in node_mapping.items() }
        traversed = set()
        other.add_missing(self, 0, 0, 0, rev_mapping, traversed)
        other.add_missing(self, other.next_node, self.next_node, -tunnel, rev_mapping, traversed)

        # both resulting mazes should still be equal
        assert(are_equal_mazes(my_old_picture, self.picture))
        assert(are_equal_mazes(other_old_picture, other.picture))

        print("merge resulted in: self=%i other=%i" % (self.next_node, other.next_node))
        print(self.picture)
        print(other.picture)

    # Walk our picture and that of the other rat from the given node, finding
    # mappings between any nodes that are common between the two. Mappings
    # are expressed as other_node->this_node. The rotation parameter expresses
    # the offset of the other_node's edges relative to this_node's edges.
    def add_node_mapping(
        self, other: Rat, 
        this_node: int, other_node: int,
        rotation: int,
        mapping: Dict[int, int]):

        #print("add_node_mapping(%i, %i, %i)" % (this_node, other_node, rotation))
        #print("  current mapping: %s" % mapping)

        # if this node is already mapped, we are finished
        if other_node in mapping:
            if mapping[other_node] != this_node:
                raise Exception("TODO: we do not currently handle loops")
            return

        # add this node
        mapping[other_node] = this_node

        # make sure this rat and other rat are on the same page
        edges = self.picture[this_node]
        other_edges = other.picture[other_node]
        edge_count = len(edges)
        if edge_count != len(other_edges):
            raise Exception("Confused: first rat thinks node %i is %s, "
                "but other thinks matching node %i is %s (mapping=%s)" 
                % (this_node, edges, other_node, other_edges, mapping))

        #print("  our edges: %s" % edges)
        #print("  other edges: %s" % other_edges)

        # recurse through any known edges
        for (i, subnode) in enumerate(edges):
            other_subnode = other_edges[(i + rotation) % edge_count]
            if subnode != UNKNOWN and other_subnode != UNKNOWN:
                #print("  %i maps to %i" % (subnode, other_subnode))
                this_back = self.picture[subnode].index(this_node)
                other_back = other.picture[other_subnode].index(other_node)
                subrotation = other_back - this_back
                self.add_node_mapping(other, subnode, other_subnode, subrotation, mapping)

    def ensure_next_exists(self, directions: int):
        # nothing to do if the next node already exists, except to verify the number
        # of exits
        if self.next_node != UNKNOWN:
            if len(self.picture[self.next_node]) != directions:
                raise Exception("merge in wrong place: directions=%i node=%s" %(directions, self.picture[self.next_node]))

        # create a new node and point self.next_node at it
        this_node = len(self.picture)
        self.next_node = this_node
        self.picture.append([UNKNOWN] * directions)
        self.picture[this_node][0] = self.prev_node
        if self.prev_node >= 0:
            self.picture[self.prev_node][self.prev_edge] = this_node

    # Modifies self, by adding any nodes or edges that are known to the
    # other rat but not to us.
    def add_missing(
        self, other: 'MemoryRat', 
        this_node: int, other_node: int,
        rotation: int,
        mapping: Dict[int, int],
        traversed: Set[int]):

        assert(this_node != UNKNOWN and other_node != UNKNOWN)

        if this_node != mapping[other_node]:
            print("TODO: we do not currently handle loops")

        # If we have already handled this node, do not do so again
        # (Avoid walking forever round loops)
        if this_node in traversed:
            return
        traversed.add(this_node)

        # If 'other' has edges that we do not know about, add them.
        edges = self.picture[this_node]
        other_edges = other.picture[other_node]
        edge_count = len(edges)
        assert(edge_count == len(other_edges))
        #print("merging %s into %s with rotation %i" % (other_edges, edges, rotation))
        for (i, subnode) in enumerate(edges):
            other_subnode = other_edges[(i + rotation) % edge_count]
            #print("merging %i into %i" % (other_subnode, subnode))
            if other_subnode != UNKNOWN:
                # if the other rat knows the node and we do not, add it
                if subnode == UNKNOWN:
                    # If we know the destination node, set it in our edges
                    if other_subnode in mapping:
                        #print("add missing edge %i=%i in edges %s" % (i, other_subnode, edges))
                        edges[i] = mapping[other_subnode]
                        self.fill_back_link(other, this_node, other_node, subnode, other_subnode, mapping)
                    else:
                        # Otherwise add a new node
                        new_node = len(self.picture)
                        #print("add missing node %i=%i in edges %s" % (i, new_node, edges))
                        self.picture.append([UNKNOWN] * len(other.picture[other_subnode]))
                        self.picture[new_node][0] = this_node
                        edges[i] = new_node
                        mapping[other_subnode] = new_node

                # We now know the node, even if we did not before, so recurse. (We cannot do
                # this if we do not know the relative rotation, so we do need back pointers.)
                this_subnode = edges[i]
                if (this_node in self.picture[this_subnode] 
                        and other_node in other.picture[other_subnode]):
                    this_back = self.picture[this_subnode].index(this_node)
                    other_back = other.picture[other_subnode].index(other_node)
                    subrotation = other_back - this_back
                    self.add_missing(other, this_subnode, other_subnode, subrotation, mapping, traversed)

    # This rat (Alice) has visited a node (this_subnode) before, but not from
    # this same direction as other rat (Bert), who is visiting from Bert's
    # equivalent of this_node (other_node). Bert's view of this_subnode is
    # other_subnode. This function fills in Alice's back-link from
    # this_subnode to this_node, corresponding to the already-present back-
    # link from Bert's other_subnode to other_node.    
    def fill_back_link(
        self, 
        other: 'MemoryRat',
        this_node: int,
        other_node: int,
        this_subnode: int,
        other_subnode: int,
        mapping: Dict[int, int]):

        # This is an entertainingly difficult problem. Let's call self Alice and
        # other, Bert. Alice has already visited this_subnode from a different
        # direction. We want to fill in the back-link to this_node, but we do not
        # know which of the tunnels leading from this_subnode is the one leading
        # back to this_node. We do know that Alice has never been along this tunnel,
        # so it is marked as UNKNOWN. There are special cases where we are able to work it
        # out:
        #
        # 1. Where there is only one UNKNOWN tunnel
        # 2. Where Bert and Alice have been along the same tunnel as each
        # other in this_subnode, so Alice can work out the rotation between
        # Bert and Alice's worldviews.
        # 3. Where there is only one possible way of fitting Bert's worldview
        # into Alice's, by rotating Bert's pattern into Alice's.
        #
        # However, in general this is an insoluble problem. We have to leave
        # the back_link as UNKNOWN. We could store somewhere the partial
        # extra information that Bert has given us, though it is (I think)
        # implicit in the maze without back-link, just hard to get at and use.
        #
        # TODO: for now, we always leave the back-link unfilled
        print("fill_back_link not yet implemented")

def test_memory_rat_no_loops():
    maze = SimpleMaze(random_maze(0.0, OneDimensionalLocalizer(25, 5)), False)
    rat = MemoryRat()
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    #render_graph(maze.maze(), "temp/memory_maze")
    #render_graph(rat.final_picture(), "temp/memory_picture")
    assert(are_equal_mazes(rat.final_picture(), maze.maze()))
    print("test_memory_rat_no_loops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_memory_rat_loops():
    maze = SimpleMaze(random_maze(0.5, OneDimensionalLocalizer(25, 5)), False)
    rat = MemoryRat()
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    #render_graph(maze.maze(), "temp/memory_maze_loops")
    #if len(rat.final_picture()) < 26:
    #    render_graph(rat.final_picture(), "temp/memory_picture_loops")
    #assert(are_equal_mazes(rat.final_picture(), maze.maze()))

    # are_equal_mazes just blows up out of recursion space if the final_picture
    # is too big.
    final = rat.final_picture()
    if len(final) < 100:
        assert(are_equal_mazes(final, maze.maze()))
    print("test_memory_rat_loops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    for _ in range(100):
        test_memory_rat_no_loops()
        test_memory_rat_loops()
