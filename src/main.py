from generator.dungeon import gen_map
from paint.painter import PainterConfig, create_image
from paint.FillStep import FillStep
from paint.DrawRoomsStep import DrawRoomsStep
from paint.RoomNumbersStep import RoomNumbersStep
from PIL import ImageFont
import sys
import os
import subprocess


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
    config.add_render_layer(FillStep((13, 13, 23)))
    config.add_render_layer(DrawRoomsStep(32, (77, 77, 77), (96, 0, 0)))
    config.add_render_layer(RoomNumbersStep(subFont, (48, 48, 48)))

    create_image(dungeon, config)
    open_image('Dungeon.tiff')
