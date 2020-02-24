from PIL import Image, ImageDraw
from generator.dungeon import Dungeon
from paint.config import PainterConfig
from typing import Tuple


def plot_map(dungeon: Dungeon, config: PainterConfig) -> Tuple[int, int]:
    bounds = dungeon.bounds()

    roomSize = config.roomSize
    headerSize = config.headerSize

    imageWidth = (bounds[2] - bounds[0] + 3) * roomSize
    imageHeight = (bounds[3] - bounds[1] + 3) * roomSize + headerSize

    for roomIndex, room in enumerate(dungeon.rooms):
        room.index = roomIndex
        room.pixelX = (room.x - bounds[0] + 1) * roomSize
        room.pixelY = (room.y - bounds[1] + 1) * roomSize + headerSize

        room.pixelEndX = room.pixelX + roomSize - 1
        room.pixelEndY = room.pixelY + roomSize - 1

    return imageWidth, imageHeight


def create_image(dungeon: Dungeon, config: PainterConfig) -> None:
    """Creates and saves an image of the given dungeon.

    This function can be used to crate an image of a dungeon. This
    process works by using the steps defined in the config to generate
    layers of a image, defining different properties of the map. These
    layers can then be compressed into a single layer when saved or
    saved as a layered image. If the list of steps in the config are
    empty, nothing happens.

    Parameters
    ----------
    dungeon : Dungeon
        The dungeon to create an image of.

    config : PainterConfig
        A config specifying how the image should be rendered.
    """

    if len(config.steps) == 0:
        return

    imageWidth, imageHeight = plot_map(dungeon, config)

    images = []
    for step in config.steps:
        img = Image.new('RGBA', (imageWidth, imageHeight), color=None)
        images.append(img)

        draw = ImageDraw.Draw(img)
        step.run(dungeon, img, draw)

    if not config.layeredImage:
        img = images[0]
        draw = ImageDraw.Draw(img)

        for i in range(1, len(images)):
            draw.bitmap((0, 0), images[i])

    images[0].save(config.imageName, save_all=config.layeredImage,
                   append_images=images[1:])
