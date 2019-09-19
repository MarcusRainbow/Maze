from RatInterface import Rat
from SimpleMaze import SimpleMaze

class InteractiveRat(Rat):

    # The maze asks which way we want to turn. We ask the user.
    def turn(self, directions: int) -> int:
        msg = ""
        if directions == 0:
            msg = "You are stuck. Type 0 to wait or 1 to quit: "
        elif directions == 1:
            msg = "Dead end. Type 0 to wait, 1 to reverse or 2 to quit: "
        elif directions == 2:
            msg = "Corridor. Type 0 to wait, 1 to go forward, 2 to reverse or 3 to quit: "
        else:
            msg = "%i exits. Type 0 to wait, %i to quit, or choose an exit: " % (directions, directions + 1)
        
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
    