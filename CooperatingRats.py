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

    def name(self):
        return self.id

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
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert", "Charlie"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_noloops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_loops():
    maze = MultiRatMaze(random_maze(0.1, OneDimensionalLocalizer(25, 5)), False)
    #render_graph(maze.maze(), "temp/cooperative_maze_loops")
    # print(maze.maze())
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert", "Charlie"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_loops solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_1():
    #seed(1001)  # lost error
    seed(1003)   # loops error
    maze = MultiRatMaze([[3, 1], [0, 4], [4, 3, 5], [4, 0, 6, 2], [6, 2, 5, 3, 1],
        [4, 2], [4, 3, 8], [8, 10], [7, 9, 6], [8]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_1")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_1 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_2():
    seed(1013)   # assert(edge_count == len(other_edges))
    maze = MultiRatMaze([[1, 3, 2], [0, 4], [0, 4], [4, 0, 5], [6, 2, 3, 1], [7, 3], 
        [7, 4], [10, 8, 9, 6, 5], [7], [7]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_2")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_2 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_3():
    seed(1004)   # assert(edge_count == len(other_edges))
    maze = MultiRatMaze([[2, 1, 3], [3, 4, 0, 2], [3, 1, 0], [0, 1, 2], [1, 7, 5], 
        [8, 4], [7], [4, 6, 9], [5], [10, 7]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_3")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_3 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_4():
    seed(1032)   # Inconsistent node picture
    maze = MultiRatMaze([[1, 2], [0, 2, 4], [1, 0, 3], [2], [7, 6, 1], 
        [7], [9, 4], [5, 4, 10], [9], [6, 8]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_4")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_4 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_5():
    seed(1018)
    maze = MultiRatMaze([[3], [3, 4], [4], [4, 1, 5, 6, 0], [1, 6, 3, 2],
        [3], [3, 4, 9, 8], [9], [6], [7, 6, 10]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_5")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_5 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_6():
    seed(1000)
    maze = MultiRatMaze([[3, 1], [3, 2, 0], [1, 4], [4, 6, 0, 1], [2, 3], 
        [7, 8, 6], [9, 5, 3], [9, 5], [5, 9], [8, 7, 10, 6]], False)
    # render_graph(maze.maze(), "temp/test_cooperative_rats_6")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_6 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_7():
    seed(1011)  # causes fill_back_link to fill a node whose edges are already all set
    maze = MultiRatMaze([[5, 3], [4, 2], [1], [0], [5, 9, 6, 1], [8, 0, 4],
        [10, 4], [12, 8], [7, 5], [4], [11, 6], [10], [13, 15, 7], [17, 12], 
        [18, 16], [12, 17, 18, 20], [18, 14, 21], [19, 15, 18, 13],
        [14, 17, 15, 16], [24, 21, 17], [15], [19, 16], [25, 24],
        [24], [22, 23, 19]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_7")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_7 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_8():
    seed(1019)  # Mismatch mapping nodes: [] does not match [1]
    maze = MultiRatMaze([[2], [6, 4], [3, 0, 5, 7, 4], [2], [1, 8, 2],
        [9, 2, 7], [1], [5, 10, 2, 8], [11, 4, 7], [13, 5], [14, 7], 
        [8], [17, 15], [9], [16, 10, 19], [20, 12], [14], 
        [19, 20, 22, 12], [19], [17, 18, 14], [15, 17], [23, 24], 
        [24, 17], [21], [22, 21, 25]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_8")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_8 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_9():
    seed(1122)  # Unexpectedly different rotation
    maze = MultiRatMaze([[2], [6, 4], [3, 0, 5, 7, 4], [2], [1, 8, 2],
        [9, 2, 7], [1], [5, 10, 2, 8], [11, 4, 7], [13, 5], [14, 7], 
        [8], [17, 15], [9], [16, 10, 19], [20, 12], [14], 
        [19, 20, 22, 12], [19], [17, 18, 14], [15, 17], [23, 24], 
        [24, 17], [21], [22, 21, 25]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_9")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_9 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_10():
    seed(1076)  # Alias 18 ([2, 19, 22]) does not match base 12 ([])
    maze = MultiRatMaze([[2], [3], [5, 0, 6], [1, 4], [8, 3, 5], 
        [4, 2, 7], [9, 2], [11, 5], [4, 9], [8, 6, 10], [9], 
        [7, 12, 13], [16, 17, 11], [15, 18, 14, 11], 
        [13], [13], [12], [22, 12], [13, 21], [23], [22], [24, 18], 
        [17, 25, 20], [19, 24], [21, 23]], False)
    # render_graph(maze.maze(), "temp/test_cooperative_rats_10")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_10 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_11():
    seed(1192)  # 7 is not in list
    maze = MultiRatMaze([[1, 2], [0], [4, 0], [5], [8, 2], [3, 8, 7], 
        [9], [12, 5], [4, 13, 5, 12], [13, 6], [11], [10, 15, 16], 
        [7, 8], [8, 15, 9], [16, 18], [13, 11], [14, 11], [21, 18], 
        [17, 14, 22], [24], [22, 25], [24, 17], [18, 20], [24], 
        [21, 23, 19]], False)
    #render_graph(maze.maze(), "temp/test_cooperative_rats_11")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_11 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_cooperative_rats_12():
    seed(1341)  # assert(are_equal_mazes(my_old_picture, self.picture, my_old_start, self.start))
    #seed(1758)  # assert(assert(valid_exit_count > 0))
    #seed(2032)  # Cannot calculate rotation: 9 not in [2, 4, 7, -1] or 9 not in [3, 9, 5, 7]
    maze = MultiRatMaze([[1, 2], [0], [4, 0], [5], [8, 2], [3, 8, 7], 
        [9], [12, 5], [4, 13, 5, 12], [13, 6], [11], [10, 15, 16], 
        [7, 8], [8, 15, 9], [16, 18], [13, 11], [14, 11], [21, 18], 
        [17, 14, 22], [24], [22, 25], [24, 17], [18, 20], [24], 
        [21, 23, 19]], False)
    # render_graph(maze.maze(), "temp/test_cooperative_rats_12")
    rats = [(CooperativeRat(r), 1) for r in ["Alice", "Bert"]]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, RatChatMazeInfo())
    print("test_cooperative_rats_12 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_cooperative_rats_1()
    test_cooperative_rats_2()
    test_cooperative_rats_3()
    test_cooperative_rats_4()
    test_cooperative_rats_5()
    test_cooperative_rats_6()
    test_cooperative_rats_7()
    test_cooperative_rats_8()
    test_cooperative_rats_9()
    test_cooperative_rats_10()
    test_cooperative_rats_11()
    test_cooperative_rats_12()

    for _ in range(1000):
        test_cooperative_rats_noloops()
    for i in range(371):
        print("test_cooperative_rats_loops(%i)" % i)
        test_cooperative_rats_loops()
