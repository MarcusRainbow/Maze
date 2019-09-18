import random
from RatInterface import Rat

class AlwaysLeftRat(Rat):

    # The maze asks which way we want to turn. We always turn in
    # the left-most direction. If the number of directions is one,
    # this means we return the way we came. If the number of directions
    # is zero, meaning this is a path of no return, one is out of range
    # and an error is generated. This is what we want.
    def turn(self, directions: int) -> int:
        return 1

class RandomRat(Rat):

    # The maze asks which way we want to turn. We turn in
    # a random direction, but never zero (no move) or >
    # directions (quit), unless there are no directions to go.
    def turn(self, directions: int) -> int:
        if directions == 0:
            return 1    # causes error
        elif directions == 1:
            return 1    # no choice
        else:
            return random.randrange(1, directions + 1)

