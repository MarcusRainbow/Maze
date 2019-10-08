import random
from RatInterface import Rat, MazeInfo
from MultiRatMaze import MultiRatMaze
from SimpleMaze import random_maze, render_graph
from Localizer import OneDimensionalLocalizer

# The only thing that paired rats know about is that they see another rat
# at the same location as themselves
class PairedRatMazeInfo(MazeInfo):
    def __init__(self):
        # avoid treating the first step as a hit
        self.positions = [-1, -2]
        self.prev = [-3, -4]
        self.hit_rat = [False] * 2
        self.rat = None

    def set_pos(self, pos: int, _back: int, _directions: int, rat: Rat):
        id = rat.get_id()
        if id > 1:
            raise Exception("Only two rats allowed with PairedRat")
        self.prev[id] = self.positions[id]
        self.positions[id] = pos
        
        # Have we landed on the other rat and is it going the same way as us?
        # Also avoid turning if either we or the other rat is already in process
        # of turning. We want to ensure that both rats remain in step.
        if (self.positions[0] == self.positions[1] 
                and self.prev[0] == self.prev[1]
                and not self.hit_rat[0] and not self.hit_rat[1]):
            self.hit_rat = [True] * 2

        #A = ord('A')
        #print("id=%i pos=%s prev=%s hit_rat=%s" % (id, str(chr(pos + A)), str(chr(self.prev[id] + A)), self.hit_rat))

    # Tests whether the current rat has hit another rat. Always resets
    # the state back to unhit, so hits only count once per rat.    
    def has_hit_rat(self, rat: Rat) -> bool:
        id = rat.get_id()
        hit = self.hit_rat[id]
        self.hit_rat[id] = False
        return hit

class PairedAlwaysLeftRat(Rat):

    # A paired rat has an integer id (0 or 1) so we can tell which it is
    def __init__(self, id: int):
        self.id = id

    def get_id(self) -> int:
        return self.id

    # The maze asks which way we want to turn. We always turn in
    # the left-most direction, which is 1 unless we can only go
    # backwards. The exception to this rule is when we run into
    # another rat, in which case we assume we must be in a loop
    # and both rats have to reverse back the way they came.
    def turn(self, directions: int, info: MazeInfo) -> int:
        
        # if we hit a rat, go back the way we came
        if info.has_hit_rat(self):
            return 0
        
        # otherwise behave like a standard always-left rat
        if directions > 1:
            return 1
        else:
            return 0    # dead-end or pit


def test_paired_rats_1():
    # This maze fails if the rat position is set only just before the rat moves.
    # This leads to the two rats going in different directions because the second
    # rat reverses at a different place from the first.
    maze = MultiRatMaze([[3, 2], [2, 3], [5, 0, 1, 3, 4], [0, 2, 1, 6], [5, 2], [2, 4]], False)
    render_graph(maze.maze(), "temp/paired1")
    MAX_ITER = 100
    rats = [(PairedAlwaysLeftRat(0), 2), (PairedAlwaysLeftRat(1), 3)]
    iter = maze.solve(rats, MAX_ITER, False, PairedRatMazeInfo())
    print("test_paired_rats_1 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_paired_rats_2():
    # This maze fails if there is no test that the rats are not currently hit
    # before setting the hit flags. This can lead to one rat reversing twice,
    # and not the other
    maze = MultiRatMaze([[1], [0, 2, 3, 4], [4, 1, 5], [1, 5, 4], [3, 1, 5, 2], [3, 6, 2, 4]], False)
    #render_graph(maze.maze(), "temp/paired2")
    MAX_ITER = 100
    rats = [(PairedAlwaysLeftRat(0), 2), (PairedAlwaysLeftRat(1), 3)]
    iter = maze.solve(rats, MAX_ITER, False, PairedRatMazeInfo())
    print("test_paired_rats_2 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_paired_rats_3():
    # This maze fails if the relative speeds are 2 and 3, because it means
    # that every other step the two rats march in step, so Alice catches up
    # with Bert twice on the same loop, reversing twice.
    maze = MultiRatMaze([[2, 1], [4, 3, 0], [3, 0, 4, 5], [5, 1, 6, 4, 2], [2, 3, 1], [2, 3]], False)
    #render_graph(maze.maze(), "temp/paired3")
    MAX_ITER = 150
    rats = [(PairedAlwaysLeftRat(0), 2), (PairedAlwaysLeftRat(1), 4)]
    iter = maze.solve(rats, MAX_ITER, False, PairedRatMazeInfo())
    print("test_paired_rats_3 solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_paired_rats_4():
    # This maze fails for relative speeds 1 and 2 because there are two 
    # interlocking loops, and the rats settle into a repeating ping-pong
    # between the two.
    maze = MultiRatMaze([[3, 1], [0], [4, 5], [5, 0], [2, 5], [6, 2, 3, 4]], False)
    #render_graph(maze.maze(), "temp/paired4")
    MAX_ITER = 150
    rats = [(PairedAlwaysLeftRat(0), 2), (PairedAlwaysLeftRat(1), 4)]
    iter = maze.solve(rats, MAX_ITER, False, PairedRatMazeInfo())
    print("test_paired_rats_4 solved after %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

def test_paired_rats_5():
    # This maze fails for relative speeds 1 and 2 because there are 
    # interlocking loops, and the rats settle into a repeating ping-pong
    # between them.
    maze = MultiRatMaze([[1, 2, 3], [4, 0, 2], [1, 4, 3, 0], [5, 0, 2, 4], [5, 3, 1, 6, 2], [4, 3]], False)
    render_graph(maze.maze(), "temp/paired5")
    MAX_ITER = 150
    rats = [(PairedAlwaysLeftRat(0), 1), (PairedAlwaysLeftRat(1), 2)]
    iter = maze.solve(rats, MAX_ITER, False, PairedRatMazeInfo())
    print("test_paired_rats_5 failed to solve after %i iterations" % iter)
    assert(iter == MAX_ITER + 1)

def test_paired_rats():
    maze = MultiRatMaze(random_maze(0.5, OneDimensionalLocalizer(6, 3)), False)
    #render_graph(maze.maze(), "temp/paired")
    print(maze)
    rats = [(PairedAlwaysLeftRat(0), 1), (PairedAlwaysLeftRat(1), 2)]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, PairedRatMazeInfo())
    print("test_paired_rats solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

# this fails
#[[1, 2, 3], [4, 0, 2], [1, 4, 3, 0], [5, 0, 2, 4], [5, 3, 1, 6, 2], [4, 3]]

if __name__ == "__main__":
    test_paired_rats_1()
    test_paired_rats_2()
    test_paired_rats_3()
    test_paired_rats_4()
    test_paired_rats_5()
    #for _ in range(100):
    #    test_paired_rats()
