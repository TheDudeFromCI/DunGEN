import subprocess
import os
import sys
from config import config
from random import randrange as rand
from random import shuffle
from math import sqrt, floor


class Dungeon:
    def __init__(self):
        self.rooms = []
        self.keys = []

    def add_room(self, room):
        self.rooms.append(room)

    def bounds(self):
        minX = minY = float("inf")
        maxX = maxY = float("-inf")

        for room in self.rooms:
            minX = min(minX, room.x)
            maxX = max(maxX, room.x)
            minY = min(minY, room.y)
            maxY = max(maxY, room.y)

        return (minX, minY, maxX, maxY)


class DungeonRoom:
    def __init__(self, type):
        self.type = type
        self.x = 0
        self.y = 0
        self.doors = [False, False, False, False]
        self.lockedDoors = [False, False, False, False]
        self.enemies = []
        self.items = []
        self.optional = False
        self.pathNext = None
        self.pathLast = None

    def count_doors(self, locked=False, excluding=[]):
        doors = self.lockedDoors if locked else self.doors

        count = 0
        for i in range(4):
            if i not in excluding:
                if doors[i]:
                    count += 1

        return count

    def direction_to(self, room):
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

    def locked_door_dir(self, excluding=[]):
        for i in range(4):
            if i not in excluding:
                if self.lockedDoors[i]:
                    return i
        return -1


def gen_map():
    dungeon = Dungeon()
    layout_rooms(dungeon)

    return dungeon


def get_entrance_room(rooms):
    entrance_name = config['Entrance']
    for room in rooms:
        if room.type['Name'] == entrance_name:
            return room


def get_room_type(name):
    for roomType in config['Room Types']:
        if roomType['Name'] == name:
            return roomType


def shuffle_directions(room):
    x = room.x
    y = room.y
    directions = [(x - 1, y, 0), (x + 1, y, 2), (x, y - 1, 1), (x, y + 1, 3)]
    shuffle(directions)
    return directions


def can_place_room(dungeon, pos):
    for room in dungeon.rooms:
        if room.x == pos[0] and room.y == pos[1]:
            return False

    return True


def random_room():
    while True:
        roomType = config['Room Types'][rand(len(config['Room Types']))]

        if roomType['Name'] == config['Entrance'] or roomType['Name'] == config['Exit']:
            continue

        if roomType['Optional']:
            continue

        if roomType['Max Doors'] < 2:
            continue

        return DungeonRoom(roomType)


def create_path(dungeon, length, room, depth):
    prepareLocked = False
    keyLocation = None

    while length > 0:
        nextPos = None
        for direction in shuffle_directions(room):
            if can_place_room(dungeon, direction):
                nextPos = direction

        if nextPos is None:
            return False, None

        if depth == 0 and length == 1:
            newRoom = DungeonRoom(get_room_type(config['Exit']))
        else:
            newRoom = random_room()

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
                success, branchRoom = create_path(dungeon, 1, room, depth + 1)
                if not success:
                    return False, None

                branchRoom.optional = True

            if depth == 0 and rand(4) == 0:
                success, branchRoom = create_path(
                    dungeon, rand(4) + 1, room, depth + 1)
                if not success:
                    return False, None

                prepareLocked = True
                keyLocation = branchRoom

    return True, room


def layout_rooms(dungeon):
    while True:
        room = DungeonRoom(get_room_type(config['Entrance']))
        dungeon.add_room(room)
        room.depth = 0

        success, lastRoom = create_path(dungeon, rand(15, 30), room, 0)
        if success:
            break

        dungeon.rooms = []
        dungeon.keys = []


if __name__ == '__main__':
    dungeon = gen_map()
    dungeon.name = 'The Sewers'
    dungeon.index = 2

    import painter
    painter.paint(dungeon)
