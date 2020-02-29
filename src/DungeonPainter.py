from PIL import Image, ImageDraw, ImageFont, ImageColor  # type: ignore
from typing import Tuple, List, cast, Dict
from math import sqrt, floor
from DunGEN import Dungeon, DungeonRoom, DungeonPath
from abc import ABCMeta, abstractmethod
from random import randrange as rand


class PaintableRoom:
    """
    A paintable room is a wrapper for a dungeon room which also
    contains the pixel position of the room.

    Attributes
    ----------
    room: DungeonRoom
        The room this wrapper represents.

    start: Tuple[int, int]
        The top left pixel coordinates.

    end: Tuple[int, int]
        The bottom right pixel coordinates.

    center: Tuple[float, float]
        The center pixel coordinates.

    rect: Tuple[int, int, int, int]
        A rectangle containing the start and end points.

    size: int
        The room size in pixels.
    """

    def __init__(self, room: DungeonRoom):
        """
        Parameters
        ----------
        room: DungeonRoom
            The room this wrapper represents.
        """

        self.room = room
        self.start = (0, 0)
        self.end = (0, 0)
        self.center = (0, 0)
        self.rect = (0, 0, 0, 0)
        self.size = 0


class RenderLayer(metaclass=ABCMeta):
    """
    An interface which is used to render an image layer of a dungeon.
    """

    @abstractmethod
    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """
        Renders a single image layer of a dungeon.

        Parameters
        ----------
        dungeon: Dungeon
            The dungeon which is being rendered.

        paintableRooms: Dict[DungeonRoom, PaintableRoom]
            A dictionary of wrappers which can be used to extract the
            pixel coordinates of each room.

        img: Image
            The virtual image being written to. A new, empty image is
            created for each render layer and composed at the end.

        draw: ImageDraw
            The drawing handler to rendering to the image.
        """


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

    def __init__(self) -> None:
        self.layeredImage = True
        self.roomSize = 128
        self.headerSize = 64
        self.imageName = 'Dungeon.tiff'
        self.layers: List[RenderLayer] = []

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


def plot_map(dungeon: Dungeon,
             paintableRooms: Dict[DungeonRoom, PaintableRoom],
             config: PainterConfig) -> Tuple[int, int]:
    """
    Plots the pixel position of each room on the final image, and
    generates the image size required to fully render the dungeon.
    The pixel coordinates are written to the rooms within the dungeon.

    Parameters
    ----------
    dungeon: Dungeon
        The dungeon which is being plotted.

    paintableRooms: Dict[DungeonRoom, PaintableRoom]
        A dictionary of paintable wrappers which can be used to store
        the pixel coordinates of each room.

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

    for room in dungeon.rooms:
        p = PaintableRoom(room)
        p.start = ((room.x - bounds[0] + 1) * roomSize,
                   (room.y - bounds[1] + 1) *
                   roomSize + headerSize)

        p.end = (p.start[0] + roomSize - 1,
                 p.start[1] + roomSize - 1)

        p.center = (int((p.start[0] + p.end[0]) / 2),
                    int((p.start[1] + p.end[1]) / 2))

        p.rect = (p.start[0], p.start[1],
                  p.end[0], p.end[1])

        p.size = roomSize

        paintableRooms[room] = p

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

    paintableRooms: Dict[DungeonRoom, PaintableRoom] = {}
    imageWidth, imageHeight = plot_map(dungeon, paintableRooms, config)

    images = []
    for layer in config.layers:
        img = Image.new('RGBA', (imageWidth, imageHeight), color=None)
        images.append(img)

        draw = ImageDraw.Draw(img)
        layer.render_layer(dungeon, paintableRooms, img, draw)

    if not config.layeredImage:
        for i in range(1, len(images)):
            images[0] = Image.alpha_composite(images[0], images[i])

    images[0].save(config.imageName, save_all=config.layeredImage,
                   append_images=images[1:], compression='tiff_lzw',
                   tiffinfo={317: 2, 278: 1})


def draw_dotted_line(draw: ImageDraw, start: Tuple[float, float],
                     end: Tuple[float, float], length: int,
                     color: Tuple[int, int, int], width: int) -> None:
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

    color: Tuple[int, int, int]
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
                     color: Tuple[int, int, int],
                     thickness: int = 2) -> None:
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

    def __init__(self, color: Tuple[int, int, int]) -> None:
        """
        Parameters
        ----------
        color: Tuple[int, int, int]
            The color to fill the image with.
        """

        self.color = color

    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        rect = (0, 0, img.size[0], img.size[1])
        draw.rectangle(rect, fill=self.color)


class KeysLayer(RenderLayer):
    """
    This layer renders the locked doors in the dungeon and where their
    corresponding keys are located.
    """

    def __init__(self, keyColor: Tuple[int, int, int],
                 keyRadius: int) -> None:
        """
        Parameters
        ----------
        keyColor: Tuple[int, int, int]
            The color to use when rendering key locations.

        keyRadius: int
            The size of the key pointer, in pixels.
        """

        self.keyColor = keyColor
        self.keyRadius = keyRadius

    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for key in dungeon.keys:
            keyRoom = key.keyLocation
            keyX, keyY = paintableRooms[keyRoom].center

            rect = (keyX - self.keyRadius, keyY - self.keyRadius,
                    keyX + self.keyRadius, keyY + self.keyRadius)
            draw.ellipse(rect, fill=self.keyColor)


class WallsLayer(RenderLayer):
    """
    The DrawRooms step is used to render the walls doorways which define
    the base shape of the dungeon.
    """

    def __init__(self, doorSize: int, wallColor: Tuple[int, int, int],
                 lockColor: Tuple[int, int, int]) -> None:
        """
        Parameters
        ----------
        doorSize: int
            The number of pixels to use when rendering a door opening.

        wallColor: Tuple[int, int, int]
            The color to use when rendering walls.

        lockColor: Tuple[int, int, int]
            The color to use when rendering locked doors.
        """

        self.doorSize = doorSize
        self.wallColor = wallColor
        self.lockColor = lockColor

    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for room in dungeon.rooms:
            rect = paintableRooms[room].rect
            draw_hollow_rect(draw, rect, self.wallColor)

            doorStart = (rect[2] - rect[0] - self.doorSize) / 2
            doorEnd = doorStart + self.doorSize

            s = paintableRooms[room].start
            e = paintableRooms[room].end
            if room.doors[0]:
                r1 = (s[0], s[1] + doorStart,
                      s[0] + 4, s[1] + doorEnd)
                draw.rectangle(r1, fill=(0, 0, 0, 0))

            if room.doors[1]:
                r2 = (s[0] + doorStart, s[1],
                      s[0] + doorEnd, s[1] + 4)
                draw.rectangle(r2, fill=(0, 0, 0, 0))

            if room.doors[2]:
                r3 = (e[0] - 4, s[1] + doorStart,
                      e[0], s[1] + doorEnd)
                draw.rectangle(r3, fill=(0, 0, 0, 0))

            if room.doors[3]:
                r4 = (s[0] + doorStart, e[1] - 4,
                      s[0] + doorEnd, e[1])
                draw.rectangle(r4, fill=(0, 0, 0, 0))

        for key in dungeon.keys:
            room = key.lockLocation
            door = key.lockedDoor

            paint = paintableRooms[room]
            doorStart = int(
                (paint.end[0] - paint.start[0] - self.doorSize) / 2)
            doorEnd = doorStart + self.doorSize

            s = paint.start

            if door == 2:
                s = (s[0] + paint.size, s[1])
                door = 0

            if door == 3:
                s = (s[0], s[1] + paint.size)
                door = 1

            if door == 0:
                r1 = (s[0] - 4 - 2, s[1] + doorStart,
                      s[0] + 4, s[1] + doorEnd)
                draw_hollow_rect(draw, r1, self.lockColor)

            if door == 1:
                r2 = (s[0] + doorStart, s[1] - 4 - 2,
                      s[0] + doorEnd, s[1] + 4)
                draw_hollow_rect(draw, r2, self.lockColor)


class PathLayer(RenderLayer):
    """
    The path layer renders a path along a dungeon map which the
    individual is expected to travel to reach the end. Optional rooms
    are ignored.

    A thick line is used to represent the main path while dotted lines
    represent side paths. (Used to obtain required materials)
    """

    def __init__(self, pathColor: Tuple[int, int, int]) -> None:
        """
        Parameters
        ----------
        pathColor: Tuple[int, int, int]
            The color of the path to draw.
        """

        self.pathColor = pathColor

    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        path = []
        for room in dungeon.mainPath:
            path.append(paintableRooms[room].center)

        draw.line(path, fill=self.pathColor, width=3)
        self.draw_starting_triangle(dungeon.rooms[0], dungeon,
                                    paintableRooms, draw)
        self.draw_ending_square(dungeon.rooms[-1], paintableRooms, draw)

        for sidePath in dungeon.mainPath.sidePaths:
            self.draw_side_path(sidePath, paintableRooms, draw)

    def draw_starting_triangle(self, room: DungeonRoom, dungeon: Dungeon,
                               paintableRooms: Dict[DungeonRoom, PaintableRoom],
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

        c = paintableRooms[room].center
        size = 8

        points = []

        next = dungeon.rooms[room.index + 1]
        d = room.direction_to(next)
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
                           paintableRooms: Dict[DungeonRoom, PaintableRoom],
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

        c = paintableRooms[room].center

        rect = (c[0] - 8, c[1] - 8, c[0] + 8, c[1] + 8)
        draw_hollow_rect(draw, rect, self.pathColor, thickness=4)

    def draw_side_path(self, sidePath: DungeonPath,
                       paintableRooms: Dict[DungeonRoom, PaintableRoom],
                       draw: ImageDraw) -> None:
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

        path = []
        for room in sidePath:
            path.append(paintableRooms[room].center)

        for i in range(len(path) - 1):
            draw_dotted_line(draw, path[i],
                             path[i + 1], 5, self.pathColor, 2)

        for nSidePath in sidePath.sidePaths:
            self.draw_side_path(nSidePath, paintableRooms, draw)


class RoomNumbersLayer(RenderLayer):
    """
    The layer draws the index number of each room in the top left
    corner of the room.
    """

    def __init__(self, font: ImageFont,
                 textColor: Tuple[int, int, int]) -> None:
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

    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for room in dungeon.rooms:
            roomName = str(room.index)

            if dungeon.is_room_optional(room):
                roomName += '*'

            s = paintableRooms[room].start
            draw.text((s[0] + 4, s[1] + 2),
                      roomName, fill=self.textColor, font=self.font)


class RegionLayer(RenderLayer):
    """
    The region layer is used to visualize the different region clusters
    within a dungeon. Each region is given a random color, and all rooms
    with that region are filled with that color.
    """

    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        regionColors = [(0, 0, 0)] * dungeon.region_count()
        for i in range(len(regionColors)):
            r = rand(128) + 128
            g = rand(128) + 128
            b = rand(128) + 128
            regionColors[i] = (r, g, b)

        for room in dungeon.rooms:
            rect = paintableRooms[room].rect
            draw.rectangle(rect, fill=regionColors[room.region])
            print(room.region)


class DifficultyLayer(RenderLayer):
    """
    The difficulty layer is used to render a heatmap of difficulty
    across the dungeon for each room. Difficulty is measured as a range
    of values between dark blue, meaning a difficulty of 0, to green, to
    yellow, to dark red meaning a difficulty of 1.
    """

    def get_gradient_color(self, value: float) -> Tuple[int, int, int]:
        """
        A simple function which converts a percentile value to a heatmap
        color gradient.

        Parameters
        ----------
        value: float
            The percentile.

        Returns
        -------
        An RGB color value representing the corresponding color in the
        heightmap.
        """

        col = 'hsl(' + str((1 - value) * 240) + ', 100%, 50%)'
        return cast(Tuple[int, int, int], ImageColor.getrgb(col))

    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for room in dungeon.rooms:
            rect = paintableRooms[room].rect
            col = self.get_gradient_color(room.difficulty)
            draw.rectangle(rect, fill=col)


class RoomTypeLayer(RenderLayer):
    """
    The room type layer can be used to visualize the room types for each
    room in the dungeon. The name of the room type is printed in the
    bottom left corner of the room.
    """

    def __init__(self, font: ImageFont, color: Tuple[int, int, int]) \
            -> None:
        """
        Parameters
        ----------
        font: ImageFont
            The font to use when rendering the text.

        color: Tuple
            The color of the text.
        """

        self.font = font
        self.color = color

    def render_layer(self, dungeon: Dungeon,
                     paintableRooms: Dict[DungeonRoom, PaintableRoom],
                     img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for room in dungeon.rooms:
            if room.type is None:
                continue

            text, lines = self.word_wrap(room.type.name,
                                         paintableRooms[room].size - 8)

            w, h = self.font.getsize(text)

            r = paintableRooms[room].rect
            draw.multiline_text((r[0] + 4, r[3] - h * lines - 2),
                                text, fill=self.color, font=self.font)

    def word_wrap(self, text: str, size: int) -> Tuple[str, int]:
        """
        Adds newline characters within a block of text based on the
        width of the text, in order to make it fit within the width of
        the room bounds.

        Parameters
        ----------
        text: str
            The text to word wrap.

        size: int
            The maximum width of the text in pixels.

        Returns
        -------
        A tuple containing the wrapped text and an int representing the
        number of lines.
        """

        words = text.split(' ')

        lines = 1
        output = ''
        for i in range(len(words)):
            n = output
            if n != '':
                n += ' '
            n += words[i]

            w, h = self.font.getsize(n)

            if w >= size:
                output += '\n'
                output += words[i]
                lines += 1
            else:
                output = n

        return output, lines
