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
    def __init__(self, id: str):
        self.id = id

        # internally we use a MemoryRat to do the walking and
        # recording for us. Unless we hit other rats, we behave
        # just like a MemoryRat. Call this our memory.
        self.memory = MemoryRat()

    def name(self) -> str:
        return self.id

    # The maze asks which way we want to turn. We just ask
    # our memory and do what it says.
    def turn(self, directions: int, info: MazeInfo) -> int:
        #info.debug()
        print("%s turns in one of %i directions" % (self.name(), directions))
        return self.memory.turn(directions, None)

    # Chat by merging our memory with the other rat's
    def chat(self, other: Rat, directions: int, tunnel: int):
        print("%s merging memories with %s (tunnel %i of %i)" 
            % (self.name(), other.name(), tunnel, directions))
        self.memory.merge(other.memory, directions, tunnel)

def test_cooperative_rats_noloops():
    maze = MultiRatMaze(random_maze(0.0, OneDimensionalLocalizer(25, 5)), False)
    #render_graph(maze.maze(), "temp/cooperative_maze_noloops")
    #print(maze.maze())
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert", "Charlie"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_noloops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_loops():
    #maze = MultiRatMaze(random_maze(0.5, OneDimensionalLocalizer(25, 5)), False)
    seed(1000)
    maze = MultiRatMaze([[5, 4, 1, 2], [0, 2, 6, 4, 5, 3], [0, 6, 1, 5],
        [6, 5, 1, 4, 7], [1, 7, 8, 3, 0, 6, 5], [10, 0, 7, 1, 4, 3, 9, 2, 8], 
        [4, 3, 11, 7, 10, 2, 1], [10, 8, 12, 6, 5, 4, 3, 11], [9, 12, 4, 7, 5], 
        [5, 14, 8, 12], [12, 14, 6, 13, 5, 7], [7, 14, 12, 6], 
        [9, 11, 15, 8, 10, 17, 7], [10, 15], [9, 18, 11, 10], 
        [20, 19, 16, 13, 12], [21, 15], [20, 22, 12, 19], [14, 20], 
        [15, 17, 20], [17, 23, 19, 18, 15, 25], [16, 22], [21, 17], 
        [24, 20], [23]], False)
    #render_graph(maze.maze(), "temp/cooperative_maze_noloops")
    print(maze.maze())
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert", "Charlie"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_noloops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    for _ in range(1):
        test_cooperative_rats_noloops()
        #test_cooperative_rats_loops()
