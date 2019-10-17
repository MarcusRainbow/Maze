from random import randrange, seed
from typing import List, Set, Dict, Tuple
from copy import deepcopy
from RatInterface import Rat, MazeInfo
from SimpleMaze import SimpleMaze, random_maze, render_graph, are_equal_mazes
from Localizer import OneDimensionalLocalizer

UNKNOWN = -1     # node that we have not yet visited

class MemoryRat(Rat):
    """
    A rat that records internally where it has been.

    This sort of rat is good at navigating around a maze with no loops,
    which it does by marking dead-ends and avoiding going into them.
    However, loops simply appear to it as repeated sections of maze,
    so it has no way of knowing that a tunnel it previously marked as
    a dead-end is the same as the tunnel it is about to try.
    """
    def __init__(self):
        """
        Same data structure as a maze, except that unknown edges
        are labelled as -1
        """
        self.picture : List[List[int]] = []
        self.dead_ends : Set[int] = set()
        self.start = 0
        self.start_rotation = 0
        self.prev_node = UNKNOWN
        self.prev_edge = UNKNOWN
        self.next_node = UNKNOWN
        self.next_rotation = 0

    def final_picture(self) -> List[List[int]]:
        # add the final edge, which we know takes us to the exit
        result = deepcopy(self.picture)
        end = len(result)
        if self.prev_node >= 0:
            result[self.prev_node][self.prev_edge] = end
        return result

    def turn(self, directions: int, _: MazeInfo) -> int:
        """
        The maze asks which way we want to turn. We remember a picture
        of the maze as we go. This may not be accurate, because loops
        appear as repeats (we cannot tell the difference). However, it
        should help us to find the exit.
        """
        assert(directions > 0)
        
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

        # Find where we came from. (We assume that the maze has at most one
        # edge between any two nodes.) This may fail, if the maze has some
        # one-way edges or, more likely, some back edges have not been
        # filled in.
        if self.prev_node in current_node:
            back = current_node.index(self.prev_node)
        elif UNKNOWN not in current_node:
            raise Exception("No back pointer, and all edges known: prev=%i current_node=%s picture=%s"
                % (self.prev_node, current_node, self.picture))
        elif current_node.count(UNKNOWN) == 1:
            back = current_node.index(UNKNOWN)
        else:
            # We are about to make a turn, but we do not know which direction
            # because we do not have a valid back-pointer. All we can do is to
            # forget where we are and set off into the blue...
            self.prev_node = UNKNOWN
            self.prev_edge = 0
            self.next_node = UNKNOWN
            print("into the blue...")
            return randrange(directions)

        # Note that we need to return the direction
        # in the callers frame of reference, not ours
        self.prev_node = self.next_node
        self.prev_edge = valid_exit
        self.next_node = current_node[valid_exit]
        turn = (valid_exit - back) % directions
        #print("  old node: stepping to %i (%i) back=%i" % (self.next_node, turn, back))
        return turn

    def merge(self, other: Rat, directions: int, tunnel: int):
        """
        Merges the memories of two rats.
        
        This is not invoked directly by MemoryRat, but by
        multi-rat implementations such as CooperativeRat, which
        have more than one rat in the same maze, which chat and
        merge information when they meet.
        
        Memories are merged with the assumption that both rats
        started in the same place, and are now in the same
        place. Neither rat has yet been asked to turn, which means
        its current position is self.next_node (which may be UNKNOWN).

        Merging is largely symmetric, so both self and other are
        updated with a merged picture.
        """

        # Nothing to do if we already agree.
        if self.picture == other.picture:
            return

        # print("  merge(%i, %i): self=%i other=%i prev=%i other_prev=%i" 
        #     % (directions, tunnel, self.next_node, other.next_node, self.prev_node, other.prev_node))
        # print("  self: %s" % self.picture)
        # print("  other: %s" % other.picture)

        # the mazes should be the same, as far as we can see (parts may be unknown
        # in either or both)
        my_old_picture = deepcopy(self.picture)
        my_old_start = self.start
        other_old_picture = deepcopy(other.picture)
        other_old_start = other.start
        assert(are_equal_mazes(my_old_picture, other_old_picture, my_old_start, other_old_start))

        # For both our picture and the other picture, ensure that the
        # next node is represented.
        self.ensure_next_exists(directions)
        other.ensure_next_exists(directions)

        # update this rat's picture from the other, then vice-versa
        # print("   merge self from other: picture=%s" % self.picture)
        self.merge_from(other, tunnel)
        # print("   merge other from self: picture=%s" % other.picture)
        other.merge_from(self, -tunnel)
        
        # both resulting mazes should still be equal
        assert(are_equal_mazes(my_old_picture, self.picture, my_old_start, self.start))
        assert(are_equal_mazes(other_old_picture, other.picture, other_old_start, other.start))

        # print("  merge resulted in: self=%i other=%i" % (self.next_node, other.next_node))
        # print("  self: %s" % self.picture)
        # print("  other: %s" % other.picture)

    def merge_from(self, other: Rat, tunnel: int):
        """
        Single-directional merge. Self is updated but
        other is not.
        """

        # Walk both pictures from the start, trying to find mappings
        # between nodes in the two pictures. Then do the same from the end.
        # The value tuple here is (node, rotation)
        mapping: Dict[int, Tuple[int, int]] = {}
        aliases: Dict[int, Tuple[int, int]] = {}
        while True:
            rotation = other.start_rotation - self.start_rotation
            self.add_node_mapping(other, self.start, other.start, rotation, mapping, aliases)
            # print("from start: node mapping=%s aliases=%s" % (mapping, aliases))
            rotation = self.calculate_rotation(other, tunnel, mapping)
            self.add_node_mapping(other, self.next_node, other.next_node, rotation, mapping, aliases)
            # print("from end: node mapping=%s aliases=%s" % (mapping, aliases))
            if aliases:
                self.remove_aliases(aliases)
                mapping = {}
                aliases = {}
            else:
                break

        # Walk both pictures from the start, adding nodes and edges that
        # are known to other into self. Then do the same from the end.
        traversed: Set[int] = set()
        rotation = other.start_rotation - self.start_rotation
        self.add_missing(other, self.start, other.start, rotation, mapping, traversed)
        # print("  after add_missing(0): %s" % self.picture)
        rotation = self.calculate_rotation(other, tunnel, mapping)
        self.add_missing(other, self.next_node, other.next_node, rotation, mapping, traversed)
        # print("  after add_missing(end): %s" % self.picture)

    def add_node_mapping(
        self, other: Rat, 
        this_node: int, other_node: int,
        rotation: int,
        mapping: Dict[int, Tuple[int, int]],
        aliases: Dict[int, Tuple[int, int]]):
        """
        Walk our picture and that of the other rat from the given node, finding
        mappings between any nodes that are common between the two. Mappings
        are expressed as other_node->this_node. The rotation parameter expresses
        the offset of the other_node's edges relative to this_node's edges.
        """

        # if this node is already mapped to this, we are finished
        if other_node in mapping:
            (mapped_node, mapped_rotation) = mapping[other_node]
            if mapped_node == this_node:
                if (mapped_rotation - rotation) % len(self.picture[this_node]) != 0:
                    raise Exception("Unexpectedly different rotation: "
                        "mapped_rotation=%i rotation=%i this_node=%i other_node=%i "
                        "next=%i other_next=%i next_rotation=%i other_next_rotation=%i"
                        "edges=%s other_edges=%s mapping=%s aliases=%s"
                        % (mapped_rotation, rotation, this_node, other_node,
                        self.next_node, other.next_node, self.next_rotation, other.next_rotation,
                        self.picture[this_node], other.picture[other_node],
                        mapping, aliases))
                return

            # If the node is already mapped to something else, it means this
            # is a loop. Record it in the list of aliases. We then simply
            # return, on the basis that this node has already been mapped.
            aliases[this_node] = (mapped_node, rotation - mapped_rotation)
            return

        # add this node
        else:
            mapping[other_node] = (this_node, rotation)

        # make sure we are where we think we are
        edges = self.picture[this_node]
        other_edges = other.picture[other_node]
        edge_count = len(edges)
        if edge_count != len(other_edges):
            raise Exception("Mismatch mapping nodes: %s (%i) does not match %s (%i)" 
                % (edges, this_node, other_edges, other_node))

        # recurse through any known edges
        for (i, subnode) in enumerate(edges):
            other_subnode = other_edges[(i + rotation) % edge_count]
            if subnode != UNKNOWN and other_subnode != UNKNOWN:
                this_subnode_edges = self.picture[subnode]
                other_subnode_edges = other.picture[other_subnode]
                if this_node in this_subnode_edges and other_node in other_subnode_edges:
                    this_back = this_subnode_edges.index(this_node)
                    other_back = other_subnode_edges.index(other_node)
                    subrotation = other_back - this_back
                    self.add_node_mapping(other, subnode, other_subnode, subrotation, mapping, aliases)

    def calculate_rotation(self, other: Rat, tunnel: int, mapping: Dict[int, Tuple[int, int]]):
        """
        Calculate the rotation between our worldview and the other rat's. This depends on
        the nodes we each came from last, and the tunnel the other rat appeared to come
        from.
        """
        this_subnode_edges = self.picture[self.next_node]
        other_subnode_edges = other.picture[other.next_node]
        if self.prev_node not in this_subnode_edges or other.prev_node not in other_subnode_edges:
            raise Exception("Cannot calculate rotation: %i not in %s or %i not in %s"
                % (self.prev_node, this_subnode_edges, other.prev_node, other_subnode_edges))
        this_back = this_subnode_edges.index(self.prev_node)
        other_back = other_subnode_edges.index(other.prev_node)
        return tunnel + other_back - this_back

    def ensure_next_exists(self, directions: int):
        """
        The current node may be UNKNOWN, if the last move
        was down an unexplored passage. Given the number of
        passages in the next chamber, we can construct a
        new node. This avoids us having to special-case a
        move to UNKNOWN.
        """
        # nothing to do if the next node already exists
        if self.next_node != UNKNOWN:
            return

        # create a new node and point self.next_node at it
        this_node = len(self.picture)
        self.next_node = this_node
        self.picture.append([UNKNOWN] * directions)
        self.picture[this_node][0] = self.prev_node
        if self.prev_node >= 0:
            self.picture[self.prev_node][self.prev_edge] = this_node

    def add_missing(
        self, other: 'MemoryRat', 
        this_node: int, other_node: int,
        rotation: int,
        mapping: Dict[int, Tuple[int, int]],
        traversed: Set[int]):
        """
        Modifies self, by adding any nodes or edges that are known to the
        other rat but not to us.
        """

        assert(this_node != UNKNOWN and other_node != UNKNOWN)

        if other_node not in mapping:
            print("add_missing: ignoring unmapped node")
            return

        if this_node != mapping[other_node][0]:
            raise Exception("Aliases should have been removed before adding missing nodes")

        # If we have already handled this node, do not do so again
        # (Avoid walking forever round loops)
        if this_node in traversed:
            return
        traversed.add(this_node)

        # Verify that both nodes are equivalent
        edges = self.picture[this_node]
        other_edges = other.picture[other_node]
        edge_count = len(edges)
        if edge_count != len(other_edges):
            raise Exception("Mismatch adding missing nodes: %s does not match %s"
                % (edges, other_edges))

        # If 'other' has edges that we do not know about, add them.
        # print("merging %s into %s with rotation %i" % (other_edges, edges, rotation))
        for (i, subnode) in enumerate(edges):
            other_subnode = other_edges[(i + rotation) % edge_count]
            # print("merging %i into %i" % (other_subnode, subnode))
            if other_subnode != UNKNOWN:
                # if the other rat knows the node and we do not, add it
                if subnode == UNKNOWN:
                    # If we know the destination node, set it in our edges
                    if other_subnode in mapping:
                        edges[i] = mapping[other_subnode][0]
                        self.fill_back_link(other, this_node, other_node, edges[i], other_subnode, mapping)
                    else:
                        # Otherwise add a new node
                        new_node = len(self.picture)
                        self.picture.append([UNKNOWN] * len(other.picture[other_subnode]))
                        self.picture[new_node][0] = this_node
                        edges[i] = new_node
                        mapping[other_subnode] = (new_node, 0)

                # we may now know the node, even if we did not before, so recurse
                this_subnode = edges[i]
                this_subnode_edges = self.picture[this_subnode]
                other_subnode_edges = other.picture[other_subnode]
                if this_node in this_subnode_edges and other_node in other_subnode_edges:
                    this_back = this_subnode_edges.index(this_node)
                    other_back = other_subnode_edges.index(other_node)
                    subrotation = other_back - this_back
                    self.add_missing(other, this_subnode, other_subnode, subrotation, mapping, traversed)

    def fill_back_link(
        self, 
        other: 'MemoryRat',
        this_node: int,
        other_node: int,
        this_subnode: int,
        other_subnode: int,
        mapping: Dict[int, Tuple[int]]):
        """
        This rat (Alice) has visited a node (this_subnode) before, but not from
        this same direction as other rat (Bert), who is visiting from Bert's
        equivalent of this_node (other_node). Bert's view of this_subnode is
        other_subnode. This function fills in Alice's back-link from
        this_subnode to this_node, corresponding to the already-present back-
        link from Bert's other_subnode to other_node. 
        """   

        # This is an entertainingly difficult problem. Let's call self Alice and
        # other, Bert. Alice has already visited this_subnode from a different
        # direction. We want to fill in the back-link to this_node, but we do not
        # know which of the tunnels leading from this_subnode is the one leading
        # back to this_node. We do know that Alice has never been along this tunnel,
        # so it is marked as UNKNOWN. There are special cases where we are able to work it
        # out:
        #
        # 1. Where the backlink already exists
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
        this_edges = self.picture[this_subnode]
        if this_node in this_edges:
            return  # backlink already exists
        
        # If there are no possible locations, this is not necessarily an error. It can
        # happen because this_node is an alias of one of the edges in this_edges.
        if UNKNOWN not in this_edges:
            return

        # nothing we can do if the other node does not have the edge
        other_edges = other.picture[other_subnode]
        if other_node not in other_edges:
            return
        other_offset = other_edges.index(other_node)

        # look for a shared tunnel, and use it to set the rotation
        for i, other_edge in enumerate(other_edges):
            if other_edge != UNKNOWN and other_edge in mapping:
                mapped_edge, _ = mapping[other_edge]
                if mapped_edge in this_edges:
                    j = this_edges.index(mapped_edge)
                    this_offset = (j - i + other_offset) % len(this_edges)
                    this_edges[this_offset] = this_node
                    return

        # If we get to here, it was not possible to set the back link.
        # However, in practice the most common reason is that this is
        # the end node, which add_node_mapping has already mapped self
        # to other, and we are walking from the start. We are just
        # about to walk from the end, which will fill in the back link anyway.
        print("fill_back_link failed: this=%s node=%i other=%s other_node=%i mapping=%s"
            % (this_edges, this_node, other_edges, other_edge, mapping))

    def remove_aliases(self, aliases: Dict[int, Tuple[int, int]]):
        """
        The picture contains some nodes that are represented separately but
        are in fact aliases of each other. Remove the aliased nodes, replacing
        them with their base nodes. We may also need to update the other
        member variables in MemoryRat if these refer to aliases rather than 
        base nodes.
        """

        # keep going until there are no aliases left to remove
        while aliases:
            # print("    remove_aliases: %s" % aliases)
            # print("    picture: %s" % self.picture)

            # redirect all alias edges to their base nodes
            for edges in self.picture:
                for i, edge in enumerate(edges):
                    if edge in aliases:
                        edges[i], _ = aliases[edge]

            # print("    redirected: %s" % self.picture)
            
            # merge all alias nodes into their base nodes, then kill them by
            # setting their edges to empty.
            further_aliases: Dict[int, Tuple[int, int]] = {}
            checked: Set[int] = set()
            for alias, (base, rotation) in aliases.items():
                undo = []
                if not self.merge_nodes(alias, base, rotation, further_aliases, undo, checked):
                    raise Exception("Cannot merge nodes: %i to %i in %s" % (alias, base, self.picture))
                self.picture[alias] = []

            # print("    merged: %s" % self.picture)

            # If any alias nodes are marked as dead ends, transfer the knowledge
            # to the base node
            for alias, (base, _) in aliases.items():
                if alias in self.dead_ends:
                    self.dead_ends.add(base)
                    self.dead_ends.remove(alias)

            # Fix up specific member variables
            if self.prev_node in aliases:
                base, rotation = aliases[self.prev_node]
                self.prev_node = base
                edge_count = len(self.picture[base])
                self.prev_edge = (self.prev_edge + rotation) % edge_count
            if self.next_node in aliases:
                # print("update next_node: was %i from %s" % (self.next_node, aliases))
                self.next_node, rotation = aliases[self.next_node]
                self.next_rotation = self.next_rotation + rotation
            if self.start in aliases:
                self.start, self.rotation = aliases[self.start]

            # We may have generated some new aliases from the merging process
            # so loop until there are no more aliases
            aliases = further_aliases

        # TODO finish off by removing empty nodes -- effectively garbage collection.

    def merge_nodes(
        self, 
        alias: int, 
        base: int, 
        rotation: int,
        further_aliases: Dict[int, Tuple[int, int]],
        undo: List[Tuple[int, int, int]],
        checked: Set[int]) -> bool:
        """
        Merge together a base node and some alias to that node.
        
        Edges that the alias knows about and the base node does not
        are written into the base. The merging process may result in
        some new aliases, which are written into the
        further_aliases output parameter.
        """

        alias_edges = self.picture[alias]
        base_edges = self.picture[base]
        edge_count = len(base_edges)
        if len(alias_edges) != edge_count:
            # print("Alias %i (%s) does not match base %i (%s)" % (alias, alias_edges, base, base_edges))
            return False

        for i, alias_edge in enumerate(alias_edges):
            if alias_edge != UNKNOWN:
                base_offset = (i + rotation) % edge_count
                base_edge = base_edges[base_offset]
                # print("replace %i with %i (%s from %s) (%i from %i) rotation=%i edge_count=%i"
                #     % (alias_edge, base_edge, alias_edges, base_edges, i, base_offset, rotation, edge_count))
                if base_edge == UNKNOWN:
                    # print("alias %i matched unknown edge" % alias_edge)
                    base_edges[base_offset] = alias_edge
                    undo.append((base_edges, base_offset, base_edge))
                elif base_edge == alias_edge:
                    # print("alias %i matched indentical edge" % alias_edge)
                    pass    # already know about this edge
                elif len(self.picture[alias_edge]) != len(self.picture[base_edge]):
                    # print("Cannot merge edges of different lengths")
                    return False
                elif alias_edge in further_aliases:
                    # print("alias %i already mapped (1). Ignore" % alias_edge)
                    # leave for the next pass
                    pass
                elif base_edge in further_aliases:
                    # Make sure we do not create two aliases pointing at each other. In
                    # the case where there is some more complex structure, such as a
                    # cycle of three, leave sorting out the mess for a subsequent pass.
                    # print("alias %i already mapped (2). Ignore" % alias_edge)
                    pass
                elif reverse_lookup_alias(alias_edge, further_aliases):
                    # The opposite order of adding items from the test above
                    # print("alias %i already mapped (3). Ignore" % alias_edge)
                    pass 
                elif base in self.picture[alias_edge] and base in self.picture[base_edge]:
                    # Assume this is an alias we don't yet know about.
                    # We can calculate the rotation because the edge we came
                    # from is common to both alias and base. (Note we have
                    # already replaced alias with base in both edges.)
                    alias_back = self.picture[alias_edge].index(base)
                    base_back = self.picture[base_edge].index(base)
                    further_aliases[alias_edge] = (base_edge, base_back - alias_back)
                    # print("assume mapping from %i to %i" % (alias_edge, base_edge))
                elif alias in self.picture[alias_edge] and base in self.picture[base_edge]:
                    # As above, but the case where the alias has not been mapped.
                    alias_back = self.picture[alias_edge].index(alias)
                    base_back = self.picture[base_edge].index(base)
                    further_aliases[alias_edge] = (base_edge, base_back - alias_back)
                    # print("assume mapping from %i to %i" % (alias_edge, base_edge))
                else:
                    # If we get to here it means either the node we are looking at cannot
                    # be merged with the base, or that it can be but we are not sure how.
                    # try all the possible unifications, and go for whichever works.
                    if not self.merge_edges(alias_edge, base_edge, further_aliases, undo, checked):
                        # print("failed to merge %i with %i" % (alias_edge, base_edge))
                        return False
    
        return True

    def merge_edges(
        self, 
        alias: int,
        base: int,
        further_aliases: Dict[int, Tuple[int, int]],
        undo: List[Tuple[int, int, int]],
        checked: Set[int]) -> bool:
        """
        Same as merge_nodes, but where the rotation is not known.

        Tries every possible rotation of the set of edges. Returns
        true if there is a valid rotation, otherwise undoes what it
        has done and returns false.
        """

        # print("merge_edges: %i -> %i (%s -> %s)" 
        #     % (alias, base, self.picture[alias], self.picture[base]))

        # avoid checking a node we have already investigated
        if alias in checked:
            # print("already checked %i" % alias)
            return True
        checked.add(alias)

        # Try every possible rotation
        edge_count = len(self.picture[alias])
        for rotation in range(edge_count):
            # print("rotation: %i" % rotation)
            nested_aliases = further_aliases.copy()
            nested_undo = undo[:]
            if self.merge_nodes(alias, base, rotation, nested_aliases, nested_undo, checked):
                further_aliases[alias] = (base, rotation)
                undo = nested_undo
                # do not recursively collect further aliases
                # print("successfully matched %i" % alias)
                return True     # Currently we accept the first valid match.
            
            # undo anything that was set by the previous merge
            self.undo_merge(nested_undo)
        
        checked.remove(alias)
        # print("failed to match %i" % alias)
        return False    # no rotation works

    def undo_merge(self, undo: List):
        for (node, offset, restore) in undo:
            self.picture[node][offset] = restore

def reverse_lookup_alias(edge: int, aliases: Dict[int, Tuple[int, int]]) -> bool:
    for _, (value, _) in aliases.items():
        if edge == value:
            return True
    return False

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
