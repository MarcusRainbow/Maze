from abc import ABC, abstractmethod

class MazeInfo(ABC):

    """
    First the maze says where each rat is, by calling set_pos for each.
    Then each rat decides where to move to, by responding to turn (see Rat
    interface below). As each rat moves, the maze invokes invalidate_pos
    as the rats disappear into a tunnel. To sum up:
    
    * set_pos, as each rat appears in the next chamber
    * turn, as each rat decides where to go
    * invalidate_pos, as each rat disappears into a tunnel
    """
    
    @abstractmethod
    def set_pos(self, pos: int, back: int, directions: int, rat: 'Rat'):
        """
        Allows the maze to set the position of the current node. Also
        pass in the direction we entered the current node (back), the
        number of exits from the current node, and the current rat.
        """
        pass

    @abstractmethod
    def invalidate_pos(self, rat: 'Rat'):
        """
        Allows the maze to invalidate the position of the given rat.

        For example, this is invoked when a rat sets off down a tunnel
        but has not yet arrived at the next chamber.
        """
        pass

class Rat(ABC):
    """
    Interfact that must be implemented by a rat that walks round a maze.
    """

    @abstractmethod
    def turn(self, directions: int, info: MazeInfo) -> int:
        """
        The maze asks which way we want to turn.
        The directions parameter says how many possible directions
        you can go from the current junction, including back the
        way we came. The return value is the direction we want to go.
        A return value of zero means go back the way we came. 
        One means the left-most direction (unless there is only one
        direction, backwards). A return value of directions minus one
        is the right-most direction. A return value outside this range
        results in an error.
        
        The info parameter gives information about the maze or other rats.
        It can be ignored by simple rats, or those which are playing
        a game where the form of the maze is unknown.
        """
        pass
