class FillStep:
    """
    The FillStep operation simply fills the image with a given color. Often
    used for setting the background color.
    """

    def __init__(self, color):
        self.color = color

    def run(self, dungeon, img, draw):
        rect = (0, 0, img.size[0], img.size[1])
        draw.rectangle(rect, fill=self.color)
