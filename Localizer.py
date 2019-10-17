from abc import ABC, abstractmethod
from random import randrange

class Localizer(ABC):
    """
    When generating a maze, we need to find the next point to
    step to. A maze can be completely non-local -- all points are
    equally accessible, or it can be localized in some number of
    spatial dimensions. For example, a 2d-one-step localiser has a
    choice of four possible points to step to in the general case
    where it is in the middle of the maze.
    """

    @abstractmethod
    def node_count(self) -> int:
        """
        How many nodes does this localizer support
        """
        pass

    @abstractmethod
    def random_step(self, step_from: int, include_exit: bool) -> int:
        """
        Find the next node to step to in some random direction from
        the given node. Allows a step to the exit only if include_exit
        is true and the localizer also allows it.
        """
        pass

class NonLocalLocalizer(Localizer):
    """
    A localizer that does no localization. It allows steps to 
    anywhere, regardless of where we start
    """

    def __init__(self, maze_size: int):
        self.maze_size = maze_size

    def node_count(self) -> int:
        return self.maze_size

    def random_step(self, step_from: int, include_exit: bool) -> int:
        end = self.maze_size + (1 if include_exit else 0)
        return randrange(0, end)

class OneDimensionalLocalizer(Localizer):
    """
    A localizer that allows steps to a point within some distance 
    of the step_from point, where the maze is considered to be 
    one-dimensional.
    """

    def __init__(self, maze_size: int, max_step: int):
        self.maze_size = maze_size
        self.max_step = max_step

    def node_count(self) -> int:
        return self.maze_size

    def random_step(self, step_from: int, include_exit: bool) -> int:
        assert step_from < self.maze_size
        end = self.maze_size - (0 if include_exit else 1)
        left = max(0, step_from - self.max_step)
        right = min(end, step_from + self.max_step) + 1
        #print("step_from = %i right = %i left = %i" % (step_from, left, right))
        assert right - left >= self.max_step
        return randrange(left, right)

class TwoDimensionalOneStepLocalizer(Localizer):
    """
    A localizer that allows steps to a point within one step in two
    dimensions, except near the edges. Only allow a step to the exit
    from the top right hand point. The maze must be of a size that
    is exactly divisible by the width.
    """

    def __init__(self, maze_size: int, maze_width: int):
        assert maze_size % maze_width == 0
        self.maze_size = maze_size
        self.maze_width = maze_width
        self.maze_height = maze_size // maze_width

    def node_count(self) -> int:
        return self.maze_size

    def random_step(self, step_from: int, include_exit: bool) -> int:
        assert step_from < self.maze_size

        x = step_from % self.maze_width
        at_left = x == 0
        at_right = x == self.maze_width - 1
        y = step_from // self.maze_width
        at_base = y == 0
        at_top = y == self.maze_height - 1
    
        # if we are at the top right corner and can exit, do so
        # with probability 1/3
        if at_top and at_right and include_exit:
            if randrange(0, 3) == 0:
                return self.maze_size

        # generate a step of 0=up 1=left 2=down 3=right
        if at_top:
            step = random_step_top(at_left, at_right)
        elif at_base:
            step = random_step_top(at_left, at_right)
            if step == 2:
                step = 0   # convert down to up
        elif at_right:
            step = randrange(0, 3)  # up, left or down
        elif at_left:
            step = randrange(0, 3)  # up, left or down
            if step == 1:
                step = 3   # convert left to right
        else:
            step = randrange(0, 4)  # up, left, down or right 
        
        #print("step_from=%i step=%i at_top=%s at_base=%s at_left=%s at_right=%s" %
        #    (step_from, step, at_top, at_base, at_left, at_right))

        if step % 2 == 0:   # up or down
            return step_from + self.maze_width * (1 - step)
        else:               # left or right
            return step_from + step - 2

def random_step_top(at_left: bool, at_right: bool) -> int:
    if at_left:
        return randrange(2, 4)  # down or right
    elif at_right:
        return randrange(1, 3)  # left or down
    else:
        return randrange(1, 4)  # left, down or right

def test_non_local_localizer():
    localizer = NonLocalLocalizer(10)
    step = localizer.random_step(0, False)
    assert step >= 0 and step < 10
    step = localizer.random_step(0, True)
    assert step >= 0 and step <= 10

def test_1d_localizer():
    localizer = OneDimensionalLocalizer(10, 3)
    step = localizer.random_step(0, False)
    assert step >= 0 and step <= 3
    step = localizer.random_step(5, False)
    assert step >= 2 and step <= 8
    step = localizer.random_step(9, False)
    assert step >= 6 and step <= 9
    step = localizer.random_step(9, True)
    assert step >= 6 and step <= 10

def test_2d_localizer():
    localizer = TwoDimensionalOneStepLocalizer(9, 3)
    step = localizer.random_step(0, False)  # bottom left
    assert step == 1 or step == 3
    step = localizer.random_step(1, False)  # bottom edge
    assert step == 0 or step == 2 or step == 4
    step = localizer.random_step(2, False)  # bottom right
    assert step == 1 or step == 5
    step = localizer.random_step(3, False)  # left edge
    assert step == 0 or step == 4 or step == 6
    step = localizer.random_step(4, False)  # center
    assert step == 1 or step == 3 or step == 5 or step == 7
    step = localizer.random_step(5, False)  # right edge
    assert step == 2 or step == 4 or step == 8
    step = localizer.random_step(6, False)  # top left
    assert step == 7 or step == 3
    step = localizer.random_step(7, False)  # top edge
    assert step == 4 or step == 6 or step == 8
    step = localizer.random_step(8, False)  # top right
    assert step == 7 or step == 5
    step = localizer.random_step(8, True)   # top right allowing exit
    assert step == 7 or step == 5 or step == 9

if __name__ == "__main__":
    for i in range(10):
        test_non_local_localizer()
        test_1d_localizer()
        test_2d_localizer()