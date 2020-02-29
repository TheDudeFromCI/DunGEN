from DunGEN import RoomType
from typing import Tuple, List


def room(name: str, difficulty: int, priority: int,
         requiresEnemy: bool = False) -> RoomType:
    roomType = RoomType()
    roomType.name = name
    roomType.difficulty = difficulty / 100
    roomType.priority = priority
    roomType.requiresEnemy = requiresEnemy
    return roomType


def entrance_room(name: str, difficulty: int, priority: int) -> RoomType:
    roomType = room(name, difficulty, priority)
    roomType.isEntrance = True
    return roomType


def exit_room(name: str, difficulty: int, priority: int) -> RoomType:
    roomType = room(name, difficulty, priority)
    roomType.isExit = True
    return roomType


def get_room_types() -> List[RoomType]:
    return [
        entrance_room('Empty Entrance', 0, 1),

        exit_room('Tank Boss', 0, 1),
        exit_room('Use Enviroment Boss', 0, 1),
        exit_room('Tons-O-Bullets Boss', 0, 1),
        exit_room('Minion Caller Boss', 0, 1),

        room('Kill Specific Enemy', 10, 2, requiresEnemy=True),
        room('Kill All Eneies', 17, 2, requiresEnemy=True),
        room('Waves of Enemies', 25, 1, requiresEnemy=True),

        room('Wait & Shoot Timing Puzzle', 7, 4),
        room('Move Secret Block Puzzle', 10, 5),
        room('Red Light/Green Timing Puzzle', 12, 4),
        room('Shoot/put in Order Puzzle', 11, 3),
        room('Move & Shoot Type Timing Puzzle', 15, 4),

        room('Spike Ball Trap', 14, 3),
        room('Buzzsaw Trap', 22, 3),
        room('Flame Thrower Trap', 17, 3),
        room('Drop out Floor Trap', 31, 3),
        room('Deadly Fake Item', 37, 1),

        room('Empty Room', 1, 12),
        room('Hallway', 3, 10),
        room('Simple Maze', 8, 5),
        room('Complex Maze', 18, 2),
    ]
