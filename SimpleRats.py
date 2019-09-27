import random
from RatInterface import Rat, MazeInfo

class AlwaysLeftRat(Rat):

    # The maze asks which way we want to turn. We always turn in
    # the left-most direction, which is 1 unless we can only go
    # backwards. If the number of directions is zero, meaning this
    # is a path of no return, zero is out of range
    # and an error is generated. This is what we want.
    def turn(self, directions: int, _: MazeInfo) -> int:
        if directions > 1:
            return 1
        else:
            return 0    # dead-end or pit

class RandomRat(Rat):

    # The maze asks which way we want to turn. We turn in
    # a random direction, but never >= directions (quit),
    # unless there are no directions to go.
    def turn(self, directions: int, _: MazeInfo) -> int:
        if directions == 0:
            return 0    # causes error
        else:
            return random.randrange(0, directions)

