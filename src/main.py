from PIL import ImageFont  # type: ignore
import sys
import os
import subprocess
import DungeonPainter
import DunGEN
from DunGEN import GeneratorConfig, RoomType
from DungeonPainter import PainterConfig

BACKGROUND_COLOR = (13, 13, 13)
WALL_COLOR = (77, 77, 77)
ROOM_NUMBER_COLOR = (48, 48, 48)
LOCKED_DOOR_COLOR = (96, 0, 0)
KEY_COLOR = (128, 96, 0)
PATH_COLOR = (76, 76, 0)
ROOM_NUMBER_FONT = ImageFont.truetype('Seagram tfb.ttf', 16)


def open_image(filename: str) -> None:
    if sys.platform.startswith('linux'):
        open_cmd = 'xdg-open'
    if sys.platform.startswith('win32'):
        open_cmd = 'start'
    if sys.platform.startswith('darwin'):
        open_cmd = 'open'

    filename = os.getcwd() + os.path.sep + filename
    subprocess.run([open_cmd, filename], check=True)


def get_dungeon_config() -> GeneratorConfig:
    dungeonConfig = GeneratorConfig()

    roomType = RoomType()
    roomType.name = 'Downward Stairway Entrance'
    roomType.isEntrance = True
    dungeonConfig.add_room_type(roomType)

    roomType = RoomType()
    roomType.name = 'Boss'
    roomType.isExit = True
    dungeonConfig.add_room_type(roomType)

    roomType = RoomType()
    roomType.name = 'Spiked Ball Trap'
    dungeonConfig.add_room_type(roomType)

    roomType = RoomType()
    roomType.name = 'Timing Puzzle'
    dungeonConfig.add_room_type(roomType)

    roomType = RoomType()
    roomType.name = 'Block Puzzle'
    dungeonConfig.add_room_type(roomType)

    roomType = RoomType()
    roomType.name = 'Mini Boss'
    dungeonConfig.add_room_type(roomType)

    dungeonConfig.add_layer(DunGEN.BranchingPathLayer())
    dungeonConfig.add_layer(DunGEN.AssignRegionsLayer())
    dungeonConfig.add_layer(DunGEN.AssignDifficultiesLayer())

    return dungeonConfig


def get_painter_config() -> PainterConfig:
    painterConfig = PainterConfig()
    painterConfig.layeredImage = False

    painterConfig.layers = [
        DungeonPainter.FillLayer(BACKGROUND_COLOR),
        DungeonPainter.RegionLayer(),
        DungeonPainter.DifficultyLayer(),
        DungeonPainter.WallsLayer(32, WALL_COLOR, LOCKED_DOOR_COLOR),
        DungeonPainter.RoomNumbersLayer(ROOM_NUMBER_FONT, ROOM_NUMBER_COLOR),
        DungeonPainter.PathLayer(PATH_COLOR),
        DungeonPainter.KeysLayer(KEY_COLOR, 8),
    ]

    return painterConfig


if __name__ == '__main__':

    dungeonConfig = get_dungeon_config()
    dungeon = DunGEN.gen_map(dungeonConfig)

    painterConfig = get_painter_config()
    DungeonPainter.create_image(dungeon, painterConfig)
    open_image('Dungeon.tiff')
