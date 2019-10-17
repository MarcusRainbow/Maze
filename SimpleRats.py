import random
from RatInterface import Rat, MazeInfo

class AlwaysLeftRat(Rat):
    """
    A rat that uses the classic maze strategy of always turning
    left. This works for any maze without loops.
    """ 

    def turn(self, directions: int, _: MazeInfo) -> int:
        """
        The maze asks which way we want to turn. We always turn in
        the left-most direction, which is 1 unless we can only go
        backwards. If the number of directions is zero, meaning this
        is a path of no return, zero is out of range
        and an error is generated. This is what we want.
        """
        if directions > 1:
            return 1
        else:
            return 0    # dead-end or pit

class RandomRat(Rat):
    """
    A rat that simply turns in a random direction, including
    back the way it came. This strategy will solve any finite
    maze given enough time, but it can be very slow for large
    mazes.
    """

    def turn(self, directions: int, _: MazeInfo) -> int:
        """
        The maze asks which way we want to turn. We turn in
        a random direction, but never >= directions (quit),
        unless there are no directions to go.
        """
        if directions == 0:
            return 0    # causes error
        else:
            return random.randrange(0, directions)

