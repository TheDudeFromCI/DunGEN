"""
DunGEN is a module for generating random dungeons. A dungen consists
of a grid of rooms, which can have doorways passing between them. Each
room can contain a set of properties detailing how the room should be
implemented in the final product.
"""

from typing import Tuple, Optional, Callable, List
from random import shuffle, randrange as rand


class GeneratorError(Exception):
    """
    An error which is thrown while attempting to generate a dungeon, if
    the config file is not setup correctly.
    """


class RoomType:
    """
    A room type is a set of properties which define a specific type of
    room. Multiple rooms in a dungeon can share the same room type.
    Room types are useful for purposes such as laying out trap locations,
    enemy locations, boss locations, room contents, room placement, etc.

    Attributes
    ----------
    name: str
        The name of the room type.

    optional: bool
        Whether this room should be placed on the player path (if not
        optional), or as an extra room outside of the path.

    maxDoors: int
        The maximum number of doors which are allowed to exist in this
        room type at once.

    isEntrance: bool
        Whether or not this room is allowed to be used as an entrance
        room.

    isExit: bool
        Whether or not this room is allowed to be used as an exit room.
    """

    def __init__(self):
        self.name = 'Unnamed Room'
        self.optional = False
        self.maxDoors = 4
        self.isEntrance = False
        self.isExit = False


class GeneratorConfig:
    """
    The generator config can be used to configure how dungeons should be
    generated. The generator is based largely around defining type lists
    which determine the various options which are present for what can
    be placed in a room and around a room.

    Attributes
    ----------
    roomTypes: List[RoomType]
        A list of room types which can exist within the dungeon.
    """

    def __init__(self):
        self.roomTypes = []

    def add_room_type(self, roomType: RoomType) -> None:
        """
        Adds a new room type to the this config.

        Parameters
        ----------
        roomType: RoomType
            The room type to add.
        """

        self.roomTypes.append(roomType)

    def random_room(self, search: Callable[[RoomType], bool]) \
            -> RoomType:
        """
        Returns a random room type from this config which matches the
        given search criteria.

        Parameters
        ----------
        search: Callable[RoomType, bool]
            The search filter to use when deciding what room types can
            be returned. All room types for which this functions returns
            true are considered.

        Returns
        -------
        A random room type within the given search range, or None if
        there are no room types which match the search.

        Rasis
        -----
        GeneratorError
            If no room types match the search function.
        """

        remaining = list(filter(search, self.roomTypes))
        shuffle(remaining)

        if len(remaining) > 0:
            return remaining[0]

        raise GeneratorError


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

    def get_room_at(self, x: int, y: int) -> Optional[DungeonRoom]:
        """
        Gets the room at the given coordinates.

        Parameters
        ----------
        x: int
            The x position of the room.

        y: int
            The y position of the room.

        Returns
        -------
        The room at the given position, or None if there is no room
        with the given coords.
        """

        for room in self.rooms:
            if room.x == x and room.y == y:
                return room


def gen_map(config: GeneratorConfig) -> Dungeon:
    """
    Creates a new, randomized dungeon as specified by the config object.

    Parameters
    ----------
    config: GeneratorConfig
        The config for how the dungeon should be generated.

    Returns
    -------
    The generated dungeon.
    """

    dungeon = Dungeon()

    while True:
        room = DungeonRoom(config.random_room(lambda type:
                                              type.isEntrance))
        dungeon.add_room(room)
        room.depth = 0

        lastRoom = __create_path(dungeon, rand(15, 30), room, config)
        if lastRoom != None:
            break

        dungeon.rooms = []
        dungeon.keys = []

    return dungeon


def __shuffle_directions(x: int, y: int) -> List[Tuple[int, int, int]]:
    """
    Creates a list of room positions which touch the given room
    coordates. The list is returned in a randomized order.

    Parameters
    ----------
    x: int
        The x position of the room.

    y: int
        The y position of the room.

    Returns
    -------
    The list of new possible room positions in random order. The first
    two values of the room position tuple refer to the x and y
    coordinates, while the third value is the direction to that room
    from the given room coords.
    """

    directions = [(x - 1, y, 0), (x, y - 1, 1), (x + 1, y, 2), (x, y + 1, 3)]
    shuffle(directions)
    return directions


def __create_path(dungeon: Dungeon, length: int, room: DungeonRoom,
                  config: GeneratorConfig, depth: int = 0) \
        -> Optional[DungeonRoom]:
    """
    An internal function which generates a random path starting at, but
    not including, the given room. New rooms are added to the dungeon,
    and cannot be placed over existing rooms. This function may call
    itself recursively to add additional branching paths.

    Parameters
    ----------
    dungeon: Dungeon
        The dungeon to add the rooms to.

    length: int
        The length of the path to generate.

    room: DungeonRoom
        The starting room. This is not part of the path, but determines
        where the path should start from.

    config: GeneratorConfig
        The config to use when generating this path.

    depth: int
        How deep the path should be. This is used internally for
        counting depth while running recursively. This is the depth
        value assigned to all rooms which are generated by this path.
        Nested paths use a depth of +1 for each recursive layer.

    Returns
    -------
    The last room which was generated by this path. If the path could
    not be successfully generated, the last room will return None. If
    the path fails to generate, this function does not currently clean
    up the rooms which it generated.

    #TODO Clean up rooms to avoid generating a new dungeon from scratch.
    """

    prepareLocked = False
    keyLocation = None
    while length > 0:
        nextPos = None
        for direction in __shuffle_directions(room.x, room.y):
            if dungeon.get_room_at(direction[0], direction[1]) == None:
                nextPos = direction

        if nextPos is None:
            return None

        if depth == 0 and length == 1:
            newRoom = DungeonRoom(config.random_room(lambda type:
                                                     type.isExit))
        else:
            newRoom = DungeonRoom(config.random_room(lambda type:
                                                     not type.isEntrance
                                                     and not type.isExit))

        dungeon.add_room(newRoom)
        newRoom.depth = depth

        room.doors[nextPos[2]] = True
        newRoom.doors[(nextPos[2] + 2) % 4] = True

        if prepareLocked:
            prepareLocked = False

            room.lockedDoors[nextPos[2]] = True
            newRoom.lockedDoors[(nextPos[2] + 2) % 4] = True

            dungeon.keys.append(
                {'Key Location': keyLocation,
                 'Locked Room': room,
                 'Locked Door': nextPos[2]})

            keyLocation.pathNext = newRoom
            newRoom.pathLast = room
        else:
            room.pathNext = newRoom
            newRoom.pathLast = room

        newRoom.x = nextPos[0]
        newRoom.y = nextPos[1]
        room = newRoom

        length -= 1

        if length > 0:
            if rand(12) == 0:
                branchRoom = __create_path(dungeon, 1, room, config,
                                           depth=depth + 1)

                if branchRoom == None:
                    return None

                branchRoom.optional = True

            if depth == 0 and rand(4) == 0:
                branchRoom = __create_path(dungeon, rand(4) + 1, room,
                                           config, depth=depth + 1)

                if branchRoom == None:
                    return None

                prepareLocked = True
                keyLocation = branchRoom

    return room
