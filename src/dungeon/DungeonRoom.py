class DungeonRoom:
    """
    A dungeon room is a single room within a dungeon, containing a set
    of properties for how that room should be handled with respect to
    other rooms and the dungeon as a whole.

    Attributes
    ----------
    x: int
        The x position of the room, relative to the the starting room,
        where one room to the left of the starting room has an x = 1.

    y: int
        The y position of the room, relative to the the starting room,
        where one room to the bottom of the starting room has an y = 1.

    index: int
        The index of the room within the dungeon. Each room in a dungeon
        has a unquie index starting at 0 for the starting room. Index
        values are consecutive.

    doors: Tuple[bool, bool, bool, bool]
        A tuple representing the door states of each of the four walls
        of the function. Doors[0] is the west door, Doors[1] is the
        north door, 2 is east, and 3 is south. A value of true means
        this wall contains a doorway.

    lockedDoors: Tuple[bool, bool, bool, bool]
        A tuple which is used to determine if a door is locked or not.
        this value works in union with the 'doors' attribute.

    pathNext: DungeonRoom
        A pointer to the next room in the dungeon which a player should
        move to from this room. If the player is required to backtrace,
        the next room may not touch this room. However, it should always
        touch a room that the player has access to.

    depth: int
        If a dungeon uses backtracking to retrieve keys or items, side
        paths are given a depth of +1 from the depth of the room they
        branched off from. The main path always has a depth of 0.

    optional: bool
        Whether or not this room is on the required path to complete the
        dungeon. If true, this room can be skipped entirely to reach
        the end. If false, this room must be entered at least once to
        complete the dungeon.

    type:
        The type of room this is. A room type is assigned by the config
        to allow a room to share a set of meta properties for how the
        room should be generated or handled. Multiple rooms may have
        the same type and their type properties shared.
    """

    def __init__(self, type):
        self.x = 0
        self.y = 0
        self.index = 0
        self.doors = [False, False, False, False]
        self.lockedDoors = [False, False, False, False]
        self.pathNext = None
        self.depth = 0
        self.optional = False
        self.type = type

    def direction_to(self, room: 'DungeonRoom') -> int:
        """
        Returns the directional value, 0 - 3, when moving from this room
        to the next room. If the rooms are not touching, a value of -1
        is returned.

        Returns
        -------
        The directional value, or -1 if the rooms are not touching. A
        value of -1 is also returned if the room is undefined.
        """

        if room == None:
            return -1

        if room.x == self.x:
            if room.y == self.y - 1:
                return 1
            if room.y == self.y + 1:
                return 3
        if room.y == self.y:
            if room.x == self.x - 1:
                return 0
            if room.x == self.x + 1:
                return 2

        return -1
