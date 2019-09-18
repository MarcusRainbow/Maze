from abc import ABC, abstractmethod

class Rat(ABC):

    # The maze asks which way we want to turn.
    # The directions parameter says how many possible directions
    # you can go from the current junction, including back the
    # way we came. The return value is the direction we want to go.
    # Zero means stay still. One means the left-most direction.
    # A return value equal to the number of directions is the right-most
    # direction, in other words back the way we came. A return value
    # outside this range results in an error. 
    @abstractmethod
    def turn(self, directions: int) -> int:
        pass

