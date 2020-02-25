from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
from math import sqrt, floor
from DunGEN import Dungeon, DungeonRoom
from abc import ABCMeta, abstractmethod
from random import randrange as rand


class RenderLayer(metaclass=ABCMeta):
    """
    An interface which is used to render an image layer of a dungeon.
    """

    @abstractmethod
    def render_layer(self, dungeon: Dungeon, img: Image,
                     draw: ImageDraw) -> None:
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


def draw_dotted_line(draw: ImageDraw, start: Tuple[int, int],
                     end: Tuple[int, int], length: int, color,
                     width: int):
    """
    Draws a dotted line between two points.

    Parameters
    ----------
    draw: ImageDraw
        The drawing handler to use.

    start: Tuple[int, int]
        The first end point of the line.

    end: Tuple[int, int]
        The second end point of the line.

    length: int
        The length, in pixels, of each dashed line segment along the
        line. This is also used as the number of pixels between dashes.

    color
        The color to render the line segments with.

    width: int
        The width of the line in pixels.
    """

    delta = end[0] - start[0], end[1] - start[1]

    distance = sqrt(delta[0] ** 2 + delta[1] ** 2)
    steps = floor(distance / length / 2 + 0.5)
    vel = (delta[0] / steps / 2, delta[1] / steps / 2)

    pos = start
    for i in range(steps):
        p1 = pos[0] + vel[0], pos[1] + vel[1]
        p2 = p1[0] + vel[0], p1[1] + vel[1]
        draw.line([p1, p2], fill=color, width=width)
        pos = p2


def draw_hollow_rect(draw: ImageDraw, rect: Tuple[int, int, int, int],
                     color, thickness: int = 2) -> None:
    """
    Fills a rectanglular area with a given color, but erases the inside,
    leaving an outline with a completely transparent inside.

    Parameters
    ----------
    draw: ImageDraw
        The drawing handler.

    rect: Tuple[int, int, int, int]
        The bounds of the rectangle. The bounds are in the format
        (x1, y1, x2, y2), where the points define the edge coordinates.
        The second point lies outside of the rectangle bounds.

    color
        The color of the rectangle.

    thickness: int
        How thick to make the line in pixels. Defaults to 2.
    """

    draw.rectangle(rect, fill=color)
    rect = (rect[0] + 2, rect[1] + 2, rect[2] - 2, rect[3] - 2)
    draw.rectangle(rect, fill=(0, 0, 0, 0))


class FillLayer(RenderLayer):
    """
    The FillStep operation simply fills the image with a given color.
    Often used for setting the background color.
    """

    def __init__(self, color):
        """
        Parameters
        ----------
        color
            The color to fill the image with.
        """

        self.color = color

    def render_layer(self, dungeon: Dungeon, img: Image,
                     draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        rect = (0, 0, img.size[0], img.size[1])
        draw.rectangle(rect, fill=self.color)


class KeysLayer(RenderLayer):
    """
    This layer renders the locked doors in the dungeon and where their
    corresponding keys are located.
    """

    def __init__(self, keyColor, keyRadius: int):
        """
        Parameters
        ----------
        keyColor
            The color to use when rendering key locations.

        keyRadius: int
            The size of the key pointer, in pixels.
        """

        self.keyColor = keyColor
        self.keyRadius = keyRadius

    def render_layer(self, dungeon: Dungeon, img: Image,
                     draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for key in dungeon.keys:
            keyRoom = key['Key Location']

            keyX = (keyRoom.pixelX + keyRoom.pixelEndX) / 2
            keyY = (keyRoom.pixelY + keyRoom.pixelEndY) / 2

            rect = (keyX - self.keyRadius, keyY - self.keyRadius,
                    keyX + self.keyRadius, keyY + self.keyRadius)
            draw.ellipse(rect, fill=self.keyColor)


class WallsLayer(RenderLayer):
    """
    The DrawRooms step is used to render the walls doorways which define
    the base shape of the dungeon.
    """

    def __init__(self, doorSize: int, wallColor, lockColor):
        """
        Parameters
        ----------
        doorSize: int
            The number of pixels to use when rendering a door opening.

        wallColor
            The color to use when rendering walls.

        lockColor
            The color to use when rendering locked doors.
        """

        self.doorSize = doorSize
        self.wallColor = wallColor
        self.lockColor = lockColor

    def render_layer(self, dungeon: Dungeon, img: Image,
                     draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for room in dungeon.rooms:
            rect = (room.pixelX, room.pixelY, room.pixelEndX, room.pixelEndY)
            draw_hollow_rect(draw, rect, self.wallColor)

            doorStart = (rect[2] - rect[0] - self.doorSize) / 2
            doorEnd = doorStart + self.doorSize

            if room.doors[0]:
                rect = (room.pixelX, room.pixelY + doorStart,
                        room.pixelX + 4, room.pixelY + doorEnd)
                draw.rectangle(rect, fill=(0, 0, 0, 0))

            if room.doors[1]:
                rect = (room.pixelX + doorStart, room.pixelY,
                        room.pixelX + doorEnd, room.pixelY + 4)
                draw.rectangle(rect, fill=(0, 0, 0, 0))

            if room.doors[2]:
                rect = (room.pixelEndX - 4, room.pixelY + doorStart,
                        room.pixelEndX, room.pixelY + doorEnd)
                draw.rectangle(rect, fill=(0, 0, 0, 0))

            if room.doors[3]:
                rect = (room.pixelX + doorStart, room.pixelEndY - 4,
                        room.pixelX + doorEnd, room.pixelEndY)
                draw.rectangle(rect, fill=(0, 0, 0, 0))

        for room in dungeon.rooms:
            if not (room.lockedDoors[0] or room.lockedDoors[1]):
                continue

            rect = (room.pixelX, room.pixelY, room.pixelEndX, room.pixelEndY)
            doorStart = (rect[2] - rect[0] - self.doorSize) / 2
            doorEnd = doorStart + self.doorSize

            if room.lockedDoors[0]:
                rect = (room.pixelX - 4 - 2, room.pixelY + doorStart,
                        room.pixelX + 4, room.pixelY + doorEnd)
                draw_hollow_rect(draw, rect, self.lockColor)

            if room.lockedDoors[1]:
                rect = (room.pixelX + doorStart, room.pixelY - 4 - 2,
                        room.pixelX + doorEnd, room.pixelY + 4)
                draw_hollow_rect(draw, rect, self.lockColor)


class PathLayer(RenderLayer):
    """
    The path layer renders a path along a dungeon map which the
    individual is expected to travel to reach the end. Optional rooms
    are ignored.

    A thick line is used to represent the main path while dotted lines
    represent side paths. (Used to obtain required materials)
    """

    def __init__(self, pathColor):
        """
        Parameters
        ----------
        pathColor
            The color of the path to draw.
        """

        self.pathColor = pathColor

    def render_layer(self, dungeon: Dungeon, img: Image,
                     draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        room = dungeon.rooms[0]
        mainPath = [((room.pixelX + room.pixelEndX) / 2,
                     (room.pixelY + room.pixelEndY) / 2)]

        while room.pathNext != None:
            next = room.pathNext

            if next.depth == 0:
                mainPath.append(((next.pixelX + next.pixelEndX) / 2,
                                 (next.pixelY + next.pixelEndY) / 2))
            else:
                next = self.draw_side_path(room, draw)

            room = next

        draw.line(mainPath, fill=self.pathColor, width=3)

        self.draw_starting_triangle(dungeon.rooms[0], draw)
        self.draw_ending_square(dungeon.rooms[-1], draw)

    def draw_starting_triangle(self, room: DungeonRoom,
                               draw: ImageDraw) -> None:
        """
        Internal function for rendering the starting triangle arrow.

        Parameters
        ----------
        room: DungeonRoom
            The room to draw the arrow in.

        draw: ImageDraw
            The drawing handler.
        """

        c = ((room.pixelX + room.pixelEndX) / 2,
             (room.pixelY + room.pixelEndY) / 2)
        size = 8

        points = []

        d = room.direction_to(room.pathNext)
        if d == 0:
            points.append((c[0] + size, c[1] - size))
            points.append((c[0] + size, c[1] + size))
            points.append((c[0] - size, c[1]))
        if d == 1:
            points.append((c[0] - size, c[1] + size))
            points.append((c[0] + size, c[1] + size))
            points.append((c[0], c[1] - size))
        if d == 2:
            points.append((c[0] - size, c[1] + size))
            points.append((c[0] - size, c[1] - size))
            points.append((c[0] + size, c[1]))
        if d == 3:
            points.append((c[0] + size, c[1] - size))
            points.append((c[0] - size, c[1] - size))
            points.append((c[0], c[1] + size))

        draw.polygon(points, fill=self.pathColor)

    def draw_ending_square(self, room: DungeonRoom,
                           draw: ImageDraw) -> None:
        """
        Internal function for rendering the ending circle.

        Parameters
        ----------
        room: DungeonRoom
            The room to draw the circle in.

        draw: ImageDraw
            The drawing handler.
        """

        c = ((room.pixelX + room.pixelEndX) / 2,
             (room.pixelY + room.pixelEndY) / 2)

        rect = (c[0] - 8, c[1] - 8, c[0] + 8, c[1] + 8)
        draw_hollow_rect(draw, rect, self.pathColor, thickness=4)

    def draw_side_path(self, room: DungeonRoom, draw: ImageDraw) -> None:
        """
        Internal function for rendering a side path starting at a given
        room. If another side path is discovered, this function is
        called recursively.

        Parameters
        ----------
        room: DungeonRoom
            The room who's pathNext attribute is the first room in the
            side path.

        draw: ImageDraw
            The drawing handler.
        """

        sidePath = [((room.pixelX + room.pixelEndX) / 2,
                     (room.pixelY + room.pixelEndY) / 2)]

        lastRoom = room
        branch = room.pathNext
        while branch != None and branch.depth > room.depth:
            sidePath.append(((branch.pixelX + branch.pixelEndX) / 2,
                             (branch.pixelY + branch.pixelEndY) / 2))

            lastRoom = branch
            branch = branch.pathNext

        for i in range(len(sidePath) - 1):
            draw_dotted_line(draw, sidePath[i],
                             sidePath[i + 1], 5, self.pathColor, 2)

        return lastRoom


class RoomNumbersLayer(RenderLayer):
    """
    The layer draws the index number of each room in the top left
    corner of the room.
    """

    def __init__(self, font: ImageFont, textColor):
        """
        Parameters
        ----------
        font: ImageFont
            The font to use when drawing the text.

        textColor
            The color to use when drawing the text.
        """

        self.font = font
        self.textColor = textColor

    def render_layer(self, dungeon: Dungeon, img: Image,
                     draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for room in dungeon.rooms:
            roomName = str(room.index)

            if room.optional:
                roomName += '*'

            draw.text((room.pixelX + 4, room.pixelY + 2),
                      roomName, fill=self.textColor, font=self.font)


class RegionLayer(RenderLayer):
    """
    The region layer is used to visualize the different region clusters
    within a dungeon. Each region is given a random color, and all rooms
    with that region are filled with that color.
    """

    def render_layer(self, dungeon: Dungeon, img: Image,
                     draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        regionColors = [0] * dungeon.region_count()
        for i in range(len(regionColors)):
            r = rand(128) + 128
            g = rand(128) + 128
            b = rand(128) + 128
            regionColors[i] = (r, g, b)

        for room in dungeon.rooms:
            rect = (room.pixelX, room.pixelY,
                    room.pixelEndX, room.pixelEndY)

            draw.rectangle(rect, fill=regionColors[room.region])
