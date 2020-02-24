from paint.painter import RenderLayer
from generator.dungeon import Dungeon, DungeonRoom
from PIL import Image, ImageDraw
from paint.Utils import draw_dotted_line


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
                             sidePath[i + 1], 5, self.pathColor, 1)

        return lastRoom
