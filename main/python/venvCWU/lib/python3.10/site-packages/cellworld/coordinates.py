from json_cpp import JsonObject, JsonList
from .util import *


class Coordinates(JsonObject):
    """A class representing coordinates with x and y values.

    Attributes:
        x (int): The x-coordinate.
        y (int): The y-coordinate.

    Methods:
        __init__(self, x=0, y=0):
            Initializes a Coordinates object with optional x and y values.

        __hash__(self):
            Computes the hash value of the Coordinates object based on its x and y values.

        __eq__(self, other):
            Checks if two Coordinates objects are equal by comparing their x and y values.

        __add__(self, o):
            Adds two Coordinates objects and returns a new Coordinates object as the result.

        __sub__(self, o):
            Subtracts two Coordinates objects and returns a new Coordinates object as the result.

        __neg__(self):
            Negates the x and y values of the Coordinates object and returns a new Coordinates object.

        manhattan(self, o) -> int:
            Calculates the Manhattan distance between two Coordinates objects and returns an integer.

    """
    def __init__(self,
                 x: int = 0,
                 y: int = 0):
        self.x = int(x)
        self.y = int(y)

    def __hash__(self):
        hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, o):
        c = Coordinates()
        c.x = self.x + o.x
        c.y = self.y + o.y
        return c

    def __sub__(self, o):
        c = Coordinates()
        c.x = self.x - o.x
        c.y = self.y - o.y
        return c

    def __neg__(self):
        c = Coordinates()
        c.x = -self.x
        c.y = -self.y
        return c

    def manhattan(self, o) -> int:
        """Calculate the Manhattan distance between two Coordinates objects.

        Args:
            o (Coordinates): The other Coordinates object.

        Returns:
            int: The Manhattan distance as an integer.
        """
        return abs(o.x - self.x) + abs(o.y - self.y)


class Coordinates_list (JsonList):
    """A list-like class for storing and manipulating lists of Coordinates objects.

    Attributes:
        iterable (iterable): An iterable to initialize the list with.

    Methods:
        __init__(self, iterable=None):
            Initializes a Coordinates_list object with an optional iterable of Coordinates objects.

        get_x(self):
            Extracts the x values from all Coordinates objects in the list and returns them as a list.

        get_y(self):
            Extracts the y values from all Coordinates objects in the list and returns them as a list.

    """
    def __init__(self, iterable=None):
        JsonList.__init__(self, iterable=iterable, list_type=Coordinates)

    def get_x(self):
        """Get the x values of all Coordinates objects in the list.

        Returns:
            list: A list of x values.
        """
        x = []
        for coordinates in self:
            x.append(coordinates.x)
        return x

    def get_y(self):
        """Get the y values of all Coordinates objects in the list.

        Returns:
            list: A list of y values.
        """
        y = []
        for coordinates in self:
            y.append(coordinates.y)
        return y

