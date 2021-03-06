"""
DunGEN is a module for generating random dungeons. A dungen consists
of a grid of rooms, which can have doorways passing between them. Each
room can contain a set of properties detailing how the room should be
implemented in the final product.
"""

from typing import Tuple, Optional, Callable, List, Iterator, Any
from random import shuffle, randrange as rand, random
from abc import ABCMeta, abstractmethod


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

    difficulty: float
        The difficulty cost of this room. If a room's difficulty exceeds
        this value, it cannot use this room type. A room type's
        difficulty is subtracted from the base difficulty, while
        remaining difficulty is allocated towards enemies and similar
        entities.

    priority: int
        The randomization weight of applying this room type to a room.
        Room types with a higher priority are more likely to be
        selected. Priority must be at least 1.

    requiresEnemy: bool
        If true, this room must have at least one enemy added to it in
        order for it to be placed.
    """

    def __init__(self) -> None:
        self.name = 'Unnamed Room'
        self.optional = False
        self.maxDoors = 4
        self.isEntrance = False
        self.isExit = False
        self.difficulty = 0.0
        self.priority = 1
        self.requiresEnemy = False


class EnemyType:
    """
    An enemy type is used to tell the dungeon what enemies should be
    placed within a room.

    Attributes
    ----------
    name: str
        The name of the enemy type.

    priority: int
        The randomization weight of add this enemy type to a room. Enemy
        types with a higher priority are more likely to be selected.
        Priority must be at least 1.

    difficulty: float
        The difficulty cost of this enemy.

    maxCount: int
        The maximum number of this enemy type which can be placed in a
        single room.

    endOfRegion: bool
        If true, this enemy type can only be placed in the last room
        within a region. (The room where a key is located for unlocking
        the next region, or the exit room itself.)

    requiresEnemy: List[str]
        If this list is not empty, this enemy cannot be spawned in a
        room unless at least one of these enemies is present. Enemies
        are defined by name.

    requiresRoom: List[str]
        If this list is not empty, this enemy cannot be spawned in a
        room unless the room type is in this list. Room types are
        defined by name.
    """

    def __init__(self) -> None:
        self.name = 'Unnamed Enemy'
        self.priority = 1
        self.difficulty = 0.0
        self.maxCount = 8
        self.endOfRegion = False
        self.requiresEnemy: List[str] = []
        self.requiresRoom: List[str] = []


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

    enemyTypes: List[EnemyType]
        A list of enemy types which can exist within the dungeon.

    layers: List[DungeonGENLayer]
        A list of generation layers which should be used to generate
        the dungeon.
    """

    def __init__(self) -> None:
        self.roomTypes: List[RoomType] = []
        self.enemyTypes: List[EnemyType] = []
        self.layers: List[DungeonGENLayer] = []


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

    depth: int
        If a dungeon uses backtracking to retrieve keys or items, side
        paths are given a depth of + 1 from the depth of the room they
        branched off from. The main path always has a depth of 0.

    type: Optional[RoomType]
        The type of room this is. A room type is assigned by the config
        to allow a room to share a set of meta properties for how the
        room should be generated or handled. Multiple rooms may have
        the same type and their type properties shared.

    difficulty: float
        A value between 0 and 1, inclusive, which represents how
        difficult the room is. This value is relative to the rest of the
        dungeon. The starting room of a dungeon always has a value of 0,
        while the final room always has a value of 1. If no room type
        exists with a difficulty lower than the base difficulty, the
        room type with the lowest difficulty is selected.

    region: int
        The region index of this room. A region is a group of rooms
        which can be accessed without needing to pass through a locked
        door. A room's region number is equal to the smallest number of
        locked rooms that must be crossed to reach from the starting
        room.

    enemies: List[EnemyType]
        A list of all enemies which are located within this room.
    """

    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.index = 0
        self.doors = (False, False, False, False)
        self.depth = 0
        self.type: Optional[RoomType] = None
        self.difficulty = 0.0
        self.region = 0
        self.enemies: List[EnemyType] = []

    def direction_to(self, room: 'DungeonRoom') -> int:
        """
        Returns the directional value, 0 - 3, when moving from this room
        to the next room. If the rooms are not touching, a value of - 1
        is returned.

        Returns
        -------
        The directional value, or -1 if the rooms are not touching. A
        value of - 1 is also returned if the room is undefined.
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

    def set_door(self, door: int, state: bool) -> None:
        """
        Sets whether the given door should be open or closed.

        Parameters
        ----------
        door: int
            The direction to the door. 0-3, inclusive.

        state: bool
            True if the door should be open. False otherwise.
        """

        d = self.doors

        if door == 0:
            self.doors = (state, d[1], d[2], d[3])

        if door == 1:
            self.doors = (d[0], state, d[2], d[3])

        if door == 2:
            self.doors = (d[0], d[1], state, d[3])

        if door == 3:
            self.doors = (d[0], d[1], d[2], state)

    def has_room_for(self, enemy: EnemyType) -> bool:
        """
        Checks if there is enough space in this room for another
        instance of a given enemy type. The enemy's max count attribute
        is taken into consideration as well as the enemies within this
        room.

        Parameters
        ----------
        enemy: EnemyType
            The enemy type to check for.

        Returns
        -------
        True if at least one more instance of the given enemy type can
        be added to this room. False otherwise.
        """

        count = 0

        for e in self.enemies:
            if e == enemy:
                count += 1

        return count < enemy.maxCount


class DungeonKey:
    """
    A dungeon key is a pointer for referencing a locked door-key
    location pair. This is used for determining how a player may advance
    through a dungeon.

    Attributes
    ----------
    keyLocation: DungeonRoom
        The room where the key is located.

    lockLocation: DungeonRoom
        The room containing the locked door.

    lockedDoor: int
        A direction value indicating which door within the room is
        locked.
    """

    def __init__(self, keyLocation: DungeonRoom,
                 lockLocation: DungeonRoom, lockedDoor: int) -> None:
        """
        Parameters
        ----------
        keyLocation: DungeonRoom
            The room where the key is located.

        lockLocation: DungeonRoom
            The room containing the locked door.

        lockedDoor: int
            A direction value indicating which door within the room is
            locked.
        """

        self.keyLocation: DungeonRoom = keyLocation
        self.lockLocation: DungeonRoom = lockLocation
        self.lockedDoor: int = lockedDoor


class DungeonPath:
    """
    A dungeon path is a sequence of rooms which are intended to be
    explored in a certain order. Paths can be nested for the purpose
    of side paths.

    Attributes
    ----------
    rooms: List[DungeonRoom]
        A list of rooms which make up the path.

    sidePaths: List[DungeonPath]
        A list of side paths which branch off of this path.

    optional: bool
        Whether or not this path can be skipped.
    """

    def __init__(self, optional: bool) -> None:
        self.rooms: List[DungeonRoom] = []
        self.sidePaths: List[DungeonPath] = []
        self.optional = optional

    def add_room(self, room: DungeonRoom) -> None:
        """
        Adds a new room to the end of this path.

        Parameters
        ----------
        room: DungeonRoom
            The room to add.
        """

        self.rooms.append(room)

    def add_sidepath(self, sidePath) -> None:  # type: ignore
        """
        Adds a side path to this path.

        Parameters
        ----------
        sidePath: DungeonPath
            The path to add.
        """

        self.sidePaths.append(sidePath)

    def __iter__(self) -> Iterator[DungeonRoom]:
        return self.rooms.__iter__()

    def __reversed__(self) -> Iterator[DungeonRoom]:
        return self.rooms.__reversed__()

    def __contains__(self, item: Any) -> bool:
        return item in self.rooms or item in self.sidePaths


class Dungeon:
    """
    A dungeon is a complex, maze-like structure of rooms which can be
    used for generation of levels or quests within a game.

    Attributes
    ----------
    rooms: List[DungeonRoom]
        A list of rooms in this dungeon. The index of the room within
        this list is equal to the room's index attribute.

    keys: List[DungeonKey]
        A list of keys in this dungeon.

    mainPath: DungeonPath
        The main path players must travel to get from the start of the
        dungeon to the end.
    """

    def __init__(self) -> None:
        self.rooms: List[DungeonRoom] = []
        self.keys: List[DungeonKey] = []
        self.mainPath: DungeonPath = DungeonPath(False)

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

        minX = minY = 10000000
        maxX = maxY = -10000000

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

        return None

    def region_count(self) -> int:
        """
        Counts the total number of regions in this dungeon.

        Returns
        -------
        The number of regions.
        """

        if len(self.rooms) == 0:
            return 0

        return self.rooms[-1].region + 1

    def is_room_optional(self, room: DungeonRoom) -> bool:
        """
        Checks if a room is an optional room in this dungeon. A room is
        considered optional if it does not lie along any required paths.

        Parameters
        ----------
        room: DungeonRoom
            The room to check.

        Returns
        -------
        True if at least one required path uses this room. False
        otherwise.
        """

        return self.__is_room_optional_recursive(room, self.mainPath)

    def __is_room_optional_recursive(self, room: DungeonRoom,
                                     path: DungeonPath) -> bool:
        """
        An internal, recursive function for checking if a room is an
        optional room or not. This function works by checking if a room
        lies along the given path. If not, all side paths of the given
        path are checked. If all nested paths are searched and the room
        is not in any of them, the room is considered optional. Optional
        nested side paths are not searched.

        Parameters
        ----------
        room: DungeonRoom
            The room to check for.

        path: DungeonPath
            The path to check for the room along. This path is assumed
            to be required.

        Returns
        -------
        True if the room is required along the give path or one of it's
        required side paths. False otherwise.
        """

        for r in path:
            if r == room:
                return False

        for side in path.sidePaths:
            if side.optional:
                continue

            if not self.__is_room_optional_recursive(room, side):
                return False

        return True

    def is_end_of_region(self, room: DungeonRoom) -> bool:
        """
        This method checks if a given room is the last room within a
        region or not.

        Parameters
        ----------
        room: DungeonRoom
            The room to check.

        Returns
        -------
        True if this room has a key in it, or is the exit room.
        """

        for key in self.keys:
            if key.lockLocation == room:
                return True

        return room == self.mainPath.rooms[-1]


class DungeonGENLayer(metaclass=ABCMeta):
    """
    A DungenGENLayer is a processing step which is used when generating
    a dungeon to handle what information should be added to the dungeon
    and how it should be layed out. During generation, a series of
    layers are added to the config, which are executed in the order they
    were added.
    """

    @abstractmethod
    def process_dungeon(self, dungeon: Dungeon) -> None:
        """
        This method is called by the dungeon generator in the sequence
        which the generation layers are defined by the config. This call
        is used to preform the processing.

        Parameters
        ----------
        dungeon: Dungeon
            The dungeon to process.
        """


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

    for layer in config.layers:
        layer.process_dungeon(dungeon)

    return dungeon


class BranchingPathLayer(DungeonGENLayer):
    """
    The branching path layer is used to create a series of rooms which
    fill the dungeon through the process of creating a path which relies
    on a series of side paths to continue along the main path.
    """

    def __init__(self, mainPathLength: Tuple[int, int],
                 sidePathLength: Tuple[int, int], sidePathChance: int,
                 optionalRoomChance: int) -> None:

        self.mainPathLength = mainPathLength
        self.sidePathLength = sidePathLength
        self.sidePathChance = sidePathChance
        self.optionalRoomChance = optionalRoomChance

    def process_dungeon(self, dungeon: Dungeon) -> None:
        """See DungenGENLayer for docs."""

        while True:
            room = DungeonRoom()
            dungeon.add_room(room)
            room.depth = 0

            pathLength = rand(self.mainPathLength[0], self.mainPathLength[1])
            lastRoom = self.create_path(dungeon, pathLength, room,
                                        dungeon.mainPath)
            if lastRoom is not None:
                break

            dungeon.rooms = []
            dungeon.keys = []
            dungeon.mainPath = DungeonPath(False)

    def shuffle_directions(self, x: int, y: int) -> List[Tuple[int, int, int]]:
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

        directions = [(x - 1, y, 0), (x, y - 1, 1),
                      (x + 1, y, 2), (x, y + 1, 3)]
        shuffle(directions)
        return directions

    def create_path(self, dungeon: Dungeon, length: int,
                    room: DungeonRoom, path: DungeonPath,
                    depth: int = 0) -> Optional[DungeonRoom]:
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

        path: DungeonPath
            The path which is being created.

        depth: int
            How deep the path should be. This is used internally for
            counting depth while running recursively. This is the depth
            value assigned to all rooms which are generated by this path.
            Nested paths use a depth of + 1 for each recursive layer.

        Returns
        -------
        The last room which was generated by this path. If the path could
        not be successfully generated, the last room will return None.
        """

        path.add_room(room)

        prepareLocked = False
        keyLocation = None
        while length > 0:
            nextPos = None
            for direction in self.shuffle_directions(room.x, room.y):
                if dungeon.get_room_at(direction[0], direction[1]) == None:
                    nextPos = direction

            if nextPos is None:
                return None

            newRoom = DungeonRoom()
            dungeon.add_room(newRoom)
            path.add_room(newRoom)
            newRoom.depth = depth

            room.set_door(nextPos[2], True)
            newRoom.set_door((nextPos[2] + 2) % 4, True)

            if prepareLocked:
                prepareLocked = False

                if keyLocation is not None:
                    dungeon.keys.append(DungeonKey(
                        keyLocation, room, nextPos[2]))

                    keyLocation.pathNext = newRoom
                    newRoom.pathLast = room

            newRoom.x = nextPos[0]
            newRoom.y = nextPos[1]
            room = newRoom

            length -= 1

            if length > 0:
                if self.optionalRoomChance > 0 \
                        and rand(self.optionalRoomChance) == 0:
                    sidePath = DungeonPath(True)
                    path.add_sidepath(sidePath)

                    branchRoom = self.create_path(dungeon, 1, room,
                                                  sidePath, depth=depth + 1)

                    if branchRoom is None:
                        return None

                if depth == 0 and self.sidePathChance > 0\
                        and rand(self.sidePathChance) == 0:
                    sidePath = DungeonPath(False)
                    path.add_sidepath(sidePath)

                    l = rand(self.sidePathLength[0],
                             self.sidePathLength[1])
                    branchRoom = self.create_path(dungeon, l, room,
                                                  sidePath, depth=depth + 1)

                    if branchRoom is None:
                        return None

                    prepareLocked = True
                    keyLocation = branchRoom

        return room


class AssignRegionsLayer(DungeonGENLayer):
    """
    The assign regions layer can be used to break down a dungeon into a
    series of regions based on where locked doors are located. A room's
    region number is the total number of locked doors a player must pass
    through to reach the room from the start.
    """

    def __init__(self) -> None:
        pass

    def process_dungeon(self, dungeon: Dungeon) -> None:
        """See DungenGENLayer for docs."""

        for room in dungeon.rooms:
            room.region = -1

        dungeon.mainPath.rooms[0].region = 0

        changed = True
        while changed:
            changed = False

            for room in dungeon.rooms:
                if room.region > -1:
                    continue

                for near in [(room.x - 1, room.y, 0),
                             (room.x, room.y - 1, 1),
                             (room.x + 1, room.y, 2),
                             (room.x, room.y + 1, 3)]:

                    x = near[0]
                    y = near[1]
                    d = near[2]

                    if not room.doors[d]:
                        continue

                    n = dungeon.get_room_at(x, y)
                    if n is None:
                        continue

                    if n.region == -1:
                        continue

                    for key in dungeon.keys:
                        if key.lockLocation == n:
                            if key.lockedDoor == (d + 2) % 4:
                                room.region = n.region + 1
                                changed = True
                                break

                    if room.region == -1:
                        room.region = n.region
                        changed = True


class AssignDifficultiesLayer(DungeonGENLayer):
    """
    This layer is used to generate the difficulty values for each room
    in the dungeon. This can be used to ensure a steady difficulty
    progression is made throughout the dungeon.
    """

    def __init__(self, dropoff: float, noise: float,
                 startingPoints: float) -> None:
        """
        Parameters
        ----------
        dropoff: float
            The percentage of difficulty of a room after entering a new
            region.

        noise: float
            How much noise to add to the difficulty after calculating
            the value, to encourage more diversity in rooms.

        startingPoints: float
            The starting difficulty percentage for room 0, to ensure
            early rooms aren't completely empty.
        """

        self.dropoff = dropoff
        self.noise = noise
        self.startingPoints = startingPoints

    def process_dungeon(self, dungeon: Dungeon) -> None:
        """See DungenGENLayer for docs."""

        diff = 0
        currentRegion = 0
        regionValues = [0] * (dungeon.region_count() + 1)
        for room in dungeon.rooms:
            if room.region != currentRegion:
                currentRegion = room.region
                regionValues[currentRegion] = diff

            room.difficulty = diff
            diff += 1

        diff -= 1
        regionValues[-1] = diff

        for room in dungeon.rooms:
            x1 = regionValues[room.region]
            x2 = regionValues[room.region + 1]
            n = room.difficulty

            d = (((n - x1) / (x2 - x1)) ** 2) * \
                (x2 - self.dropoff * x1) + self.dropoff * x1
            d = (d / diff) * (1 - self.startingPoints) \
                + self.startingPoints

            d += random() * 2 * self.noise - self.noise
            d = max(0, min(1, d))

            room.difficulty = d


class AssignRoomTypes(DungeonGENLayer):
    """
    This layer is used to set the room types for each room in the
    dungeon based on their location.
    """

    def __init__(self, roomTypes: List[RoomType]) -> None:
        """
        Parameters
        ----------
        roomTypes: List[RoomType]
            A list of room types which can be assigned.
        """
        self.roomTypes = roomTypes

    def process_dungeon(self, dungeon: Dungeon) -> None:
        """See DungenGENLayer for docs."""

        dungeon.mainPath.rooms[0].type = self.random_room(
            lambda x: x.isEntrance)

        dungeon.mainPath.rooms[-1].type = self.random_room(
            lambda x: x.isExit)

        for room in dungeon.rooms:
            if room.type is not None:
                continue

            try:
                room.type = self.random_room(
                    lambda x: not x.isEntrance
                    and not x.isExit
                    and x.difficulty <= room.difficulty)

            except GeneratorError:
                available = list(filter(lambda x: not x.isEntrance
                                        and not x.isExit, self.roomTypes))

                if len(available) == 0:
                    raise GeneratorError

                room.type = available[0]
                for roomType in available:
                    if roomType.difficulty < room.type.difficulty:
                        room.type = roomType

    def random_room(self, search: Callable[[RoomType], bool]) \
            -> RoomType:
        """
        Returns a random room type from this config which matches the
        given search criteria.

        Parameters
        ----------
        search: Callable[[RoomType], bool]
            The search filter to use when deciding what room types can
            be returned. All room types for which this functions returns
            true are considered.

        Returns
        -------
        A random room type within the given search range.

        Rasis
        -----
        GeneratorError
            If no room types match the search function.
        """

        remaining = list(filter(search, self.roomTypes))

        weighted: List[RoomType] = []
        for room in remaining:
            for c in range(room.priority):
                weighted.append(room)

        count = len(weighted)
        if count > 0:
            return weighted[rand(count)]

        raise GeneratorError


class EnemiesLayer(DungeonGENLayer):
    """
    This layer is used to add enemies to a dungeon based on the
    remaining difficulty score of a room after the room type is taken
    into consideration.
    """

    def __init__(self, enemyTypes: List[EnemyType]) -> None:
        """
        Parameters
        ----------
        enemyTypes: List[EnemyType]
            A list of enemy types which can be placed.
        """

        self.enemyTypes = enemyTypes

    def process_dungeon(self, dungeon: Dungeon) -> None:
        """See DungenGENLayer for docs."""

        for room in dungeon.rooms:
            if room.type is None:
                continue

            if room.type.isEntrance or room.type.isExit:
                continue

            diff = room.difficulty - room.type.difficulty

            while diff > 0:
                try:
                    enemy = self.random_enemy(lambda x:
                                              x.difficulty <= diff
                                              and room.has_room_for(x)
                                              and (not x.endOfRegion or dungeon.is_end_of_region(room))
                                              and self.meets_enemy_requirements(x, room)
                                              and self.meets_room_type_requirements(x, room))

                    room.enemies.append(enemy)
                    diff -= enemy.difficulty

                except:
                    break

            print("Room", room.index, "Enemies:")
            for enemy in room.enemies:
                print("  " + enemy.name)

    def meets_enemy_requirements(self, enemy: EnemyType, room: DungeonRoom) -> bool:
        """
        Checks if the given enemy depends on another enemy being present
        or not. If so, checks if that enemy is within the room.

        Parameters
        ----------
        enemy: EnemyType
            The enemy to check.

        room: DungeonRoom
            The room to check.

        Returns
        -------
        True if this enemy has no enemy dependencies, or if it does have
        a dependency, makes sure that enemy is within the room.
        """

        if len(enemy.requiresEnemy) == 0:
            return True

        for en in room.enemies:
            if en.name in enemy.requiresEnemy:
                return True

        return False

    def meets_room_type_requirements(self, enemy: EnemyType, room: DungeonRoom) -> bool:
        """
        Checks if the given enemy depends on a certain room type being
        used. If so, checks if the room matches that type.

        Parameters
        ----------
        enemy: EnemyType
            The enemy to check.

        room: DungeonRoom
            The room to check.

        Returns
        -------
        True if this enemy has no room dependencies, or if it does have
        a dependency, makes sure that the room matches that type.
        """

        if len(enemy.requiresRoom) == 0:
            return True

        if room.type is None:
            return False

        return room.type.name in enemy.requiresRoom

    def random_enemy(self, search: Callable[[EnemyType], bool]) \
            -> EnemyType:
        """
        Returns a random enemy type from this config which matches the
        given search criteria.

        Parameters
        ----------
        search: Callable[[EnemyType], bool]
            The search filter to use when deciding what enemy types can
            be returned. All enemy types for which this functions
            returns true are considered.

        Returns
        -------
        A random enemy type within the given search range.

        Rasis
        -----
        GeneratorError
            If no enemy types match the search function.
        """

        remaining = list(filter(search, self.enemyTypes))

        weighted: List[EnemyType] = []
        for enemy in remaining:
            for c in range(enemy.priority):
                weighted.append(enemy)

        count = len(weighted)
        if count > 0:
            return weighted[rand(count)]

        raise GeneratorError
