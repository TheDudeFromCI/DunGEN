from generator.dungeon import gen_map
from paint.config import PainterConfig
from paint.painter import create_image
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

    create_image(dungeon, PainterConfig())
    open_image('Dungeon.tiff')
