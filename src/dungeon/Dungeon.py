from typing import Tuple
from dungeon.DungeonRoom import DungeonRoom


class Dungeon:
    """
    A dungeon is a complex, maze-like structure of rooms which can be
    used for generation of levels or quests within a game.

    Attributes
    ----------
    rooms: List[DungeonRoom]
        A list of rooms in this dungeon. The index of the room within
        this list is equal to the room's index attribute.

    keys
        A list of keys in this dungeon.
    """

    def __init__(self):
        self.rooms = []
        self.keys = []

    def add_room(self, room: DungeonRoom) -> None:
        """
        Adds a new room to this dungeon. Note that a room should never
        be added to two seperate dungeons.

        Parameters
        ----------
        room: DungeonRoom
            The room to add.
        """

        room.index = len(self.rooms)
        self.rooms.append(room)

    def bounds(self) -> Tuple[int, int, int, int]:
        """
        Gets the bounds of this dungeon, based on the locations of all
        rooms.

        Returns
        -------
        A tuple containing the minX, minY, maxX, maxY bounds of the room
        list, respectively.
        """

        minX = minY = float("inf")
        maxX = maxY = float("-inf")

        for room in self.rooms:
            minX = min(minX, room.x)
            maxX = max(maxX, room.x)
            minY = min(minY, room.y)
            maxY = max(maxY, room.y)

        return (minX, minY, maxX, maxY)
