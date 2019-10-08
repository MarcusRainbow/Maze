from RatInterface import Rat, MazeInfo
from RatChat import RatChat, RatChatMazeInfo
from MultiRatMaze import MultiRatMaze
from MemoryRat import MemoryRat
from abc import ABC, abstractmethod
from typing import List
from random import randrange, seed
from SimpleMaze import random_maze, render_graph
from Localizer import OneDimensionalLocalizer

# Cooperating rats only have visibility of each maze node as they
# arrive at it. They have no way of leaving markers, or identifying
# nodes other than simply by the number of exits. However, when they
# encounter other rats, they can exchange information, which allows
# them to build up a picture of the maze. They use this picture to
# try to find the exit, by investigating the nearest unexplored
# passage.
class CooperativeRat(Rat, RatChat):

    # Rats are identified by a unique integer. This is only used for
    # debugging. The rats themselves do not treat different rats
    # differently.
    def __init__(self, id: int):
        self.id = id

        # internally we use a MemoryRat to do the walking and
        # recording for us. Unless we hit other rats, we behave
        # just like a MemoryRat. Call this our memory.
        self.memory = MemoryRat()

    def name(self):
        return "Alice" if self.id == 0 else "Bert" 

    # The maze asks which way we want to turn. We just ask
    # our memory and do what it says.
    def turn(self, directions: int, info: MazeInfo) -> int:
        #info.debug()
        return self.memory.turn(directions, None)

    # Chat by merging our memory with the other rat's
    def chat(self, other: Rat, directions: int, tunnel: int):
        #print("This rat (%i) saw %i emerging from tunnel %i of %i"
        #    % (self.id, other.id, tunnel, directions))
        self.memory.merge(other.memory, directions, tunnel)

def test_cooperative_rats_noloops():
    maze = MultiRatMaze(random_maze(0.0, OneDimensionalLocalizer(25, 5)), False)
    #render_graph(maze.maze(), "temp/cooperative_maze_noloops")
    #print(maze.maze())
    rats = [(CooperativeRat(r), 1) for r in range(3)]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_noloops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_cooperative_rats_noloops()
