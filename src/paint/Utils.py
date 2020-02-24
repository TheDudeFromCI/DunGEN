from PIL import Image, ImageDraw
from typing import Tuple
from math import sqrt, floor


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


def draw_hollow_rect(draw: ImageDraw, rect: Tuple[int, int, int, int], color, thickness: int = 2) -> None:
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
    draw.rectangle(rect, fill=(0, 0, 0,))
