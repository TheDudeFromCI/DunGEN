from paint.painter import RenderLayer
from dungeon.generator import Dungeon
from PIL import Image, ImageDraw
from paint.Utils import draw_dotted_line


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

            keyX = (keyRoom.pixelX + keyRoom.pixelEndX) / 2
            keyY = (keyRoom.pixelY + keyRoom.pixelEndY) / 2

            rect = (keyX - self.keyRadius, keyY - self.keyRadius,
                    keyX + self.keyRadius, keyY + self.keyRadius)
            draw.ellipse(rect, fill=self.keyColor)
