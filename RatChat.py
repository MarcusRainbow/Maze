from RatInterface import Rat, MazeInfo
from MultiRatMaze import MultiRatMaze
from abc import ABC, abstractmethod
from random import randrange
from SimpleMaze import random_maze, render_graph
from Localizer import OneDimensionalLocalizer

# An interface that allows rats to communicate with each other. For
# example, they may simply pull all of the maze information from the
# other rat.
class RatChat(ABC):
    # Allows a rat to chat to another rat. Both rats may be modified.
    # The intention is that the chat is symmetrical between the rats.
    # The only external information available is the number of exits
    # from the current location (and we may later add the relative
    # direction of the two rats, as each rat can see which exit the
    # other rat appeared from).
    @abstractmethod
    def chat(self, other: Rat, directions: int):
        pass

# Rats can only chat if they are in the same location as each other.
# We get both chats to listen to each other, otherwise the rats may have
# moved apart before they each have the chance to listen.
class RatChatMazeInfo(MazeInfo):
    def __init__(self):
        self.pos_by_rat = {}         # position of each rat
        self.rats_by_position = {}   # rats in each position

    def set_pos(self, pos: int, back: int, directions: int, rat: Rat):
        # remove ourselves from the previous position's list
        if rat in self.pos_by_rat:
            prev_pos = self.pos_by_rat[rat]
            assert(prev_pos != pos)
            prev_rats = self.rats_by_position[prev_pos]
            prev_rats.remove(rat)

            # if the list at this position is empty, remove it altogether
            if not prev_rats:
                del self.rats_by_position[prev_pos]
        
        # add our new position, so we can remove ourselves when we next move
        self.pos_by_rat[rat] = pos

        # if no rats already there, record ourselves as the only rat
        if pos not in self.rats_by_position:
            self.rats_by_position[pos] = [rat]
        else:
            # there's at least one rat already here. Talk to them
            rats = self.rats_by_position[pos]
            for other_rat in rats:
                assert other_rat is not rat
                rat.chat(other_rat, directions)
            
            # add ourselves to the list of rats
            rats.append(rat)

class TestChatRat(Rat, RatChat):

    def __init__(self, id: int):
        self.id = id
        self.path = []  # list of (directions, turn)

    # The maze asks which way we want to turn. This test rat
    # simply turns in a random direction, but also remembers
    # which nodes it has visited and which way it turned
    def turn(self, directions: int, _info: MazeInfo) -> int:
        go = randrange(0, directions)
        self.path.append((directions, go))
        return go

    # Chat by printing out the path each rat has taken
    def chat(self, other: Rat, directions: int):
        print("this rat (%i) ran into rat (%i):" % (self.id, other.id))
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
