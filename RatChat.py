from RatInterface import Rat, MazeInfo
from MultiRatMaze import MultiRatMaze
from abc import ABC, abstractmethod
from random import randrange
from SimpleMaze import random_maze, render_graph
from Localizer import OneDimensionalLocalizer

class RatChat(ABC):
    """
    An interface that allows rats to communicate with each other. For
    example, they may simply pull all of the maze information from the
    other rat.
    """

    @abstractmethod
    def chat(self, other: Rat, directions: int, tunnel: int):
        """
        Allows a rat to chat to another rat. Both rats may be modified.

        The intention is that the chat is symmetrical between the rats.
        The only external information available is the number of exits
        from the current location and the relative direction of the two
        rats, as the first rat can see which tunnel the second rat emerges
        from, and it can communicate this to the second rat. The tunnel
        is specified relative to the tunnel that this rat came from
        originally.
        """
        pass

class RatChatMazeInfo(MazeInfo):
    """
    Implementation of MazeInfo that allows rats at the same location
    to chat to each other.
    """
    def __init__(self):
        self.pos_by_rat = {}         # position of each rat
        self.rats_by_position = {}   # (rat, back) in each position

    def debug(self):
        for (rat, pos) in self.pos_by_rat.items():
            print("   %s at %s" % (rat.name(), str(chr(ord('A') + pos))))

    def set_pos(self, pos: int, back: int, directions: int, rat: Rat):
        # print("%s moved to %s" % (rat.name(), str(chr(ord('A') + pos))))

        # add our new position, so we can remove ourselves when we next move
        self.pos_by_rat[rat] = pos

        # if no rats already there, record ourselves as the only rat
        if pos not in self.rats_by_position:
            self.rats_by_position[pos] = [(rat, back)]
        else:
            # there's at least one rat already here. Talk to them
            rats = self.rats_by_position[pos]
            for (other_rat, other_back) in rats:
                assert other_rat is not rat
                # print("%s talking to %s at %s" % (rat.name(), other_rat.name(), str(chr(ord('A') + pos))))
                other_rat.chat(rat, directions, (other_back - back) % directions)
            
            # add ourselves to the list of rats
            rats.append((rat, back))

    def invalidate_pos(self, rat: Rat):
        # remove ourselves from the previous position's list
        if rat in self.pos_by_rat:
            prev = self.pos_by_rat[rat]
            #print("%s moved from %s" % (rat.name(), str(chr(ord('A') + prev))))
            updated = [(r, b) for (r, b) in self.rats_by_position[prev] if r is not rat]
            if updated:
                self.rats_by_position[prev] = updated
            else:
                # if the list at this position is empty, remove it altogether
                del self.rats_by_position[prev]

class TestChatRat(Rat, RatChat):

    def __init__(self, id: int):
        self.id = id
        self.path = []  # list of (directions, turn)

    def turn(self, directions: int, _info: MazeInfo) -> int:
        """
        The maze asks which way we want to turn. This test rat
        simply turns in a random direction, but also remembers
        which nodes it has visited and which way it turned
        """
        go = randrange(0, directions)
        self.path.append((directions, go))
        return go

    def chat(self, other: Rat, directions: int, tunnel: int):
        """
        Chat by printing out the path each rat has taken
        """
        print("this rat (%i) ran into rat (%i) from %i of %i:"
            % (self.id, other.id, tunnel, directions))
        print("   my path:  %s" % self.path)
        print("   her path: %s" % other.path)

def test_rat_chat():
    maze = MultiRatMaze(random_maze(0.5, OneDimensionalLocalizer(25, 5)), False)
    render_graph(maze.maze(), "temp/rat_chat")
    rats = [(TestChatRat(0), 2), (TestChatRat(1), 3), (TestChatRat(2), 4)]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_paired_rats solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_rat_chat()
