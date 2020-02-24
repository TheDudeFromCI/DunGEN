from math import sqrt, floor
from typing import Tuple
from paint.painter import RenderLayer
from generator.dungeon import Dungeon
from PIL import Image, ImageDraw


def draw_dotted_line(draw: ImageDraw, start: Tuple[int, int],
                     end: Tuple[int, int], length: int, color, width: int):
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
        The length, in pixels, of each dashed line segment along the line.
        This is also used as the number of pixels between dashes.

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

    def render_layer(self, dungeon: Dungeon, img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for key in dungeon.keys:
            keyRoom = key['Key Location']
            lockRoom = key['Locked Room']
            lockDoor = key['Locked Door']

            keyX = (keyRoom.pixelX + keyRoom.pixelEndX) / 2
            keyY = (keyRoom.pixelY + keyRoom.pixelEndY) / 2

            rect = (keyX - self.keyRadius, keyY - self.keyRadius,
                    keyX + self.keyRadius, keyY + self.keyRadius)
            draw.ellipse(rect, fill=self.keyColor)

            if lockDoor == 0:
                lockX = lockRoom.pixelX
            elif lockDoor == 2:
                lockX = lockRoom.pixelEndX
            else:
                lockX = (lockRoom.pixelX + lockRoom.pixelEndX) / 2

            if lockDoor == 1:
                lockY = lockRoom.pixelY
            elif lockDoor == 3:
                lockY = lockRoom.pixelEndY
            else:
                lockY = (lockRoom.pixelY + lockRoom.pixelEndY) / 2

            draw_dotted_line(draw, (lockX, lockY), (keyX, keyY),
                             10, self.keyColor, 3)
