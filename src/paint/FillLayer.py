from paint.painter import RenderLayer
from generator.dungeon import Dungeon
from PIL import Image, ImageDraw


class fillLayer(RenderLayer):
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

    def render_layer(self, dungeon: Dungeon, img: Image, draw: ImageDraw) -> None:
        """See RenderLayer for docs."""

        rect = (0, 0, img.size[0], img.size[1])
        draw.rectangle(rect, fill=self.color)
