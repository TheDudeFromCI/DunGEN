from PIL import Image, ImageDraw
from dungeon.dungeon import Dungeon
from typing import Tuple
from abc import ABCMeta, abstractmethod


class RenderLayer(metaclass=ABCMeta):
    """
    An interface which is used to render an image layer of a dungeon.
    """

    @abstractmethod
    def render_layer(self, dungeon: Dungeon, img: Image, draw: ImageDraw) -> None:
        """
        Renders a single image layer of a dungeon.

        Parameters
        ----------
        dungeon: Dungeon
            The dungeon which is being rendered.

        img: Image
            The virtual image being written to. A new, empty image is
            created for each render layer and composed at the end.

        draw: ImageDraw
            The drawing handler to rendering to the image.
        """

        pass


class PainterConfig:
    """
    A configuration for how a dungeon should be drawn with the painter.

    ...

    Attributes
    ----------
    layeredImage: bool
        If true, the generated image will contain a seperate layer for
        each step with a transparent background. This can be useful for
        manual editing in an image editor after. If false, the output
        image will have only a single layer, and all steps will be
        overlapped.

    roomSize: int
        The size of each room, in pixels.

    headerSize: int
        If header text is desired, this value can be used to vertically
        offset the map image to make room for the header. Set to 0 to
        disable.

    layers: List[RenderLayer]
        A list of layers which are used to print the dungeon. These are
        handled in the order in which they are listed.

    imageName: str
        Specifies the filename of the image to generate. This is where
        the image will be saved to. This filename must use a TIFF file
        extension to use layers.
    """

    def __init__(self):
        self.layeredImage = True
        self.roomSize = 128
        self.headerSize = 64
        self.imageName = 'Dungeon.tiff'
        self.layers = []

    def add_render_layer(self, layer: RenderLayer) -> None:
        """
        Appends a new render layer to use when rendering dungeons with
        this configuration.

        Parameters
        ----------
        layer: RenderLayer
            The new render layer.
        """

        self.layers.append(layer)


def plot_map(dungeon: Dungeon, config: PainterConfig) -> Tuple[int, int]:
    """
    Plots the pixel position of each room on the final image, and
    generates the image size required to fully render the dungeon.
    The pixel coordinates are written to the rooms within the dungeon.

    Parameters
    ----------
    dungeon: Dungeon
        The dungeon which is being plotted.

    config: PainterConfig
        The config to use when determining room measurements.

    Returns
    -------
    A tuple containing the width and height of the image to generate.
    """

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
    saved as a layered image. If the list of layers in the config are
    empty, nothing happens.

    Parameters
    ----------
    dungeon: Dungeon
        The dungeon to create an image of.

    config: PainterConfig
        A config specifying how the image should be rendered.
    """

    if len(config.layers) == 0:
        return

    imageWidth, imageHeight = plot_map(dungeon, config)

    images = []
    for layer in config.layers:
        img = Image.new('RGBA', (imageWidth, imageHeight), color=None)
        images.append(img)

        draw = ImageDraw.Draw(img)
        layer.render_layer(dungeon, img, draw)

    if not config.layeredImage:
        for i in range(1, len(images)):
            images[0] = Image.alpha_composite(images[0], images[i])

    images[0].save(config.imageName, save_all=config.layeredImage,
                   append_images=images[1:], compression='tiff_lzw',
                   tiffinfo={317: 2, 278: 1})
