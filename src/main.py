from dungeon.dungeon import gen_map
from paint.painter import PainterConfig, create_image
from PIL import ImageFont
import sys
import os
import subprocess


from paint.FillLayer import FillLayer
from paint.WallsLayer import WallsLayer
from paint.RoomNumbersLayer import RoomNumbersLayer
from paint.PathLayer import PathLayer
from paint.KeysLayer import KeysLayer

BACKGROUND_COLOR = (13, 13, 13)
WALL_COLOR = (77, 77, 77)
ROOM_NUMBER_COLOR = (48, 48, 48)
LOCKED_DOOR_COLOR = (96, 0, 0)
KEY_COLOR = (128, 96, 0)
PATH_COLOR = (76, 76, 0)


def open_image(filename: str) -> None:
    open_cmd = 'open'
    if sys.platform.startswith('linux'):
        open_cmd = 'xdg-open'
    if sys.platform.startswith('win32'):
        open_cmd = 'start'

    filename = os.getcwd() + os.path.sep + filename
    subprocess.run([open_cmd, filename], check=True)


if __name__ == '__main__':
    dungeon = gen_map()
    dungeon.name = 'The Sewers'
    dungeon.index = 2

    mainFont = ImageFont.truetype('Seagram tfb.ttf', 24)
    subFont = ImageFont.truetype('Seagram tfb.ttf', 16)

    config = PainterConfig()
    config.layeredImage = False

    config.add_render_layer(FillLayer(BACKGROUND_COLOR))

    config.add_render_layer(WallsLayer(32, WALL_COLOR, LOCKED_DOOR_COLOR))
    config.add_render_layer(RoomNumbersLayer(subFont, ROOM_NUMBER_COLOR))
    config.add_render_layer(PathLayer(PATH_COLOR))
    config.add_render_layer(KeysLayer(KEY_COLOR, 8))

    create_image(dungeon, config)
    open_image('Dungeon.tiff')
