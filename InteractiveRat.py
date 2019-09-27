from RatInterface import Rat, MazeInfo
from SimpleMaze import SimpleMaze

class InteractiveRat(Rat):

    # The maze asks which way we want to turn. We ask the user.
    def turn(self, directions: int, _: MazeInfo) -> int:
        msg = ""
        if directions == 0:
            msg = "You are stuck. Type 0 to quit: "
        elif directions == 1:
            msg = "Dead end. Type 0 to reverse or 1 to quit: "
        elif directions == 2:
            msg = "Corridor. Type 0 to reverse, 1 to go forward, or 2 to quit: "
        else:
            msg = "%i exits. Type 0 to reverse, 1 to go left, etc: " % directions
        
        turn = input(msg)
        return int(turn)

def test_interactive_rat():
    rat = InteractiveRat()
    maze = SimpleMaze([[1, 3], [2], [3, 0]], True)
    MAX_ITER = 1000
    iter = maze.solve(rat, MAX_ITER)
    print("test_interactive_rat solved in %i iterations" % iter)
    assert(iter > 0 and iter < MAX_ITER)

if __name__ == "__main__":
    test_interactive_rat()
    