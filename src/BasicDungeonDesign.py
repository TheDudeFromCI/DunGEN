from DunGEN import RoomType, EnemyType
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


def enemy(name: str, difficulty: int, priority: int, maxCount: int = 8,
          endOfRegion: bool = False, requiresEnemy: List[str] = [],
          requiresRoom: List[str] = []) -> EnemyType:
    enemyType = EnemyType()
    enemyType.name = name
    enemyType.difficulty = difficulty / 100
    enemyType.priority = priority
    enemyType.maxCount = maxCount
    enemyType.endOfRegion = endOfRegion
    enemyType.requiresEnemy = requiresEnemy
    enemyType.requiresRoom = requiresRoom
    return enemyType


def get_enemy_types() -> List[EnemyType]:
    return [
        enemy('Tank Mini-Boss', 30, 1, maxCount=1, endOfRegion=True),
        enemy('Use Enviroment Mini-Boss', 30, 1, maxCount=1, endOfRegion=True),
        enemy('Tons-O-Bullets Mini-Boss', 30, 1, maxCount=1, endOfRegion=True),
        enemy('Minion Caller Mini-Boss', 30, 1, maxCount=1, endOfRegion=True),
        enemy('Time Survival Mini-Boss', 30, 1, maxCount=1, endOfRegion=True),

        enemy('Bombmer', 8, 2),
        enemy('Tank', 12, 2),
        enemy('Glass Cannon', 10, 3),
        enemy('Minion', 2, 5),
        enemy('Area of Effect', 15, 1),
        enemy('Quick', 8, 4),
        enemy('Ranged', 8, 4),
        enemy('General', 5, 4),
        enemy('Hidden', 12, 2),

        enemy('Support', 2, 2,
              requiresEnemy=[
                  'Tank',
                  'Glass Cannon',
                  'General',
                  'Area of Effect',
                  'Quick',
                  'Ranged'
              ]),
    ]


def get_enemy_teams() -> List[Tuple[List[str], int]]:
    return [
        (['Support', 'Tank'], 25),
        (['Support', 'Glass Cannon'], 25),
        (['Support', 'General'], 25),
        (['Support', 'Area of Effect'], 25),
        (['Support', 'Quick'], 25),
        (['Support', 'Ranged'], 25),
        (['Support', 'Tank Mini-Boss'], 25),
        (['Support', 'Use Enviroment Mini-Boss'], 25),
        (['Support', 'Tons-O-Bullets Mini-Boss'], 25),
        (['Support', 'Minion Caller Mini-Boss'], 25),
        (['Support', 'Time Survival Mini-Boss'], 25),

        (['Tank', 'Quick'], 15),
        (['Tank', 'Minion Caller Mini-Boss'], 5),
        (['Tank', 'Time Survival Mini-Boss'], 15),
        (['Tank', 'Glass Cannon'], 15),
        (['Tank', 'Area of Effect'], 15),

        (['Area of Effect', 'Minion'], 5),
        (['Area of Effect', 'Tons-O-Bullets Mini-Boss'], 35),
        (['Area of Effect', 'Minion Caller Mini-Boss'], 40),

        (['Hidden', 'Ranged'], 10),
        (['Hidden', 'Use Enviroment Mini-Boss'], 20),
        (['Hidden', 'Minion Caller Mini-Boss'], 50),

        (['Glass Cannon', 'Area of Effect'], 15),
        (['Glass Cannon', 'Tank Mini-Boss'], 10),

        (['Ranged', 'Time Survival Mini-Boss'], 5),
        (['Ranged', 'Tank Mini-Boss'], 10),

        (['Bombmer', 'Use Enviroment Mini-Boss'], 25),
        (['Bombmer', 'Minion Caller Mini-Boss'], 30),

        (['Quick', 'Tons-O-Bullets Mini-Boss'], 45),
    ]
