from abc import ABC, abstractmethod

class MazeInfo(ABC):
    # Allows the maze to set the position and direction of the
    # current node.
    @abstractmethod
    def set_pos(self, pos: int, back: int):
        pass

class Rat(ABC):

    # The maze asks which way we want to turn.
    # The directions parameter says how many possible directions
    # you can go from the current junction, including back the
    # way we came. The return value is the direction we want to go.
    # A return value of zero means go back the way we came. 
    # One means the left-most direction (unless there is only one
    # direction, backwards). A return value of directions minus one
    # is the right-most direction. A return value outside this range
    # results in an error.
    #
    # The info parameter gives information about the maze or other rats.
    # It can be ignored by simple rats, or those which are playing
    # a game where the form of the maze is unknown.
    @abstractmethod
    def turn(self, directions: int, info: MazeInfo) -> int:
        pass
