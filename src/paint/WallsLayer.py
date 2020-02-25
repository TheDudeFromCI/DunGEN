from paint.painter import RenderLayer
from dungeon.generator import Dungeon
from PIL import Image, ImageDraw
from paint.Utils import draw_hollow_rect


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

    def render_layer(self, dungeon: Dungeon, img: Image, draw: ImageDraw) -> None:
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
