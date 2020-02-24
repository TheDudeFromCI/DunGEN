from PIL import ImageFont
from paint.painter import RenderLayer
from generator.dungeon import Dungeon
from PIL import Image, ImageDraw


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

    def render_layer(self, dungeon: Dungeon, img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        for room in dungeon.rooms:
            roomName = str(room.index)

            if room.optional:
                roomName += '*'

            draw.text((room.pixelX + 4, room.pixelY + 2),
                      roomName, fill=self.textColor, font=self.font)
