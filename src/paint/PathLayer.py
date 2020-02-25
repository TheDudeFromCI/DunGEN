from paint.painter import RenderLayer
from dungeon.dungeon import Dungeon
from dungeon.DungeonRoom import DungeonRoom
from PIL import Image, ImageDraw
from paint.Utils import draw_dotted_line, draw_hollow_rect


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

    def render_layer(self, dungeon: Dungeon, img: Image, draw: ImageDraw) -> None:
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

    def draw_starting_triangle(self, room: DungeonRoom, draw: ImageDraw) -> None:
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

    def draw_ending_square(self, room: DungeonRoom, draw: ImageDraw) -> None:
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
        draw_hollow_rect(draw, rect, self.pathColor, thickness=3)

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
