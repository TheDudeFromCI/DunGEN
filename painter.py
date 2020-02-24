from PIL import Image, ImageDraw, ImageFont
from path_layer import draw_path_layer
from key_layer import draw_keys_layer
from base_layer import draw_base_layer
from number_layer import draw_numbers_layer
import sys
import os
import subprocess

ROOM_SIZE = 128
BUFFER_SIZE = 64
HEADER_SIZE = 64
BACKGROUND = (13, 13, 23)


def plot_map(dungeon):
    bounds = dungeon.bounds()
    imageWidth = (bounds[2] - bounds[0] + 1) * ROOM_SIZE + BUFFER_SIZE * 2
    imageHeight = (bounds[3] - bounds[1] + 1) * \
        ROOM_SIZE + BUFFER_SIZE * 2 + HEADER_SIZE

    for roomIndex, room in enumerate(dungeon.rooms):
        room.index = roomIndex
        room.pixelX = (room.x - bounds[0]) * ROOM_SIZE + BUFFER_SIZE
        room.pixelY = (room.y - bounds[1]) * \
            ROOM_SIZE + BUFFER_SIZE + HEADER_SIZE

        room.pixelEndX = room.pixelX + ROOM_SIZE - 1
        room.pixelEndY = room.pixelY + ROOM_SIZE - 1

    return imageWidth, imageHeight


def open_image(filename):
    open_cmd = 'open'
    if sys.platform.startswith('linux'):
        open_cmd = 'xdg-open'
    if sys.platform.startswith('win32'):
        open_cmd = 'start'

    filename = os.getcwd() + os.path.sep + filename
    subprocess.run([open_cmd, filename], check=True)


def paint(dungeon):
    imageWidth, imageHeight = plot_map(dungeon)

    img = Image.new('RGB', (imageWidth, imageHeight), color=BACKGROUND)
    layer2 = Image.new('RGBA', (imageWidth, imageHeight), color=None)
    layer3 = Image.new('RGBA', (imageWidth, imageHeight), color=None)
    layer4 = Image.new('RGBA', (imageWidth, imageHeight), color=None)

    #layer2 = layer3 = layer4 = img

    draw_base_layer(dungeon, ImageDraw.Draw(img))
    draw_numbers_layer(dungeon, ImageDraw.Draw(layer2))
    draw_keys_layer(dungeon, ImageDraw.Draw(layer3))
    draw_path_layer(dungeon, ImageDraw.Draw(layer4))

    img.save('dungeon.tiff', save_all=True, append_images=[
        layer2, layer3, layer4])
    # open_image('dungeon.tiff')
