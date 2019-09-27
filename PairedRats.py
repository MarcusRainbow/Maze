import random
from RatInterface import Rat, MazeInfo
from MultiRatMaze import MultiRatMaze
from SimpleMaze import random_maze, render_graph
from Localizer import OneDimensionalLocalizer

# The only thing that paired rats know about is that they see another rat
# at the same location as themselves
class PairedRatMazeInfo(MazeInfo):
    def __init__(self):
        self.positions = [-1] * 2
        self.hit_rat = [False] * 2
        self.rat = 0

    def set_pos(self, pos: int, back: int, rat: int):
        if rat > 1:
            raise Exception("Only two rats allowed with PairedRat")
        self.rat = rat
        self.positions[rat] = pos
        
        # have we landed on the other rat?
        if self.positions[0] == self.positions[1]:
            self.hit_rat = [True] * 2

    # Tests whether the current rat has hit another rat. Always resets
    # the state back to unhit, so hits only count once per rat.    
    def has_hit_rat(self) -> bool:
        hit = self.hit_rat[self.rat]
        self.hit_rat[self.rat] = False
        return hit

class PairedAlwaysRat(Rat):

    # The maze asks which way we want to turn. We always turn in
    # the left-most direction, which is 1 unless we can only go
    # backwards. The exception to this rule is when we run into
    # another rat, in which case we assume we must be in a loop
    # and both rats have to reverse back the way they came.
    def turn(self, directions: int, info: MazeInfo) -> int:
        
        # if we hit a rat, go back the way we came
        if info.has_hit_rat():
            return 0
        
        # otherwise behave like a standard always-left rat
        if directions > 1:
            return 1
        else:
            return 0    # dead-end or pit

def test_paired_rats():
    maze = MultiRatMaze(random_maze(0.5, OneDimensionalLocalizer(25, 5)), False)
    render_graph(maze.maze(), "temp/paired")
    rat = PairedAlwaysRat()     # stateless rat, so we only need one
    rats = [(rat, 2), (rat, 3)]
    MAX_ITER = 1000
    iter = maze.solve(rats, MAX_ITER, False, PairedRatMazeInfo())
    print("test_paired_rats solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_paired_rats()
