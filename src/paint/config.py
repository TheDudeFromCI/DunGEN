from paint.FillStep import FillStep
from paint.DrawRoomsStep import DrawRoomsStep

class PainterConfig:
    """A configuration for how a dungeon should be drawn with the painter.
    
    ...
    
    Attributes
    ----------
    layeredImage : bool
        If true, the generated image will contain a seperate layer for each
        step with a transparent background. This can be useful for manual
        editing in an image editor after. If false, the output image will
        have only a single layer, and all steps will be overlapped.
        
    roomSize : int
        The size of each room, in pixels.
    
    headerSize : int
        If header text is desired, this value can be used to vertically offset
        the map image to make room for the header. Set to 0 to disable.
    
    steps : list
        A series of steps which are used to print the dungeon. These are handled in the order in which they are listed.
        
    imageName : str
        Specifies the filename of the image to generate. This is where the image
        will be saved to. This filename must use a TIFF file extension to use
        layers.
    """
    
    def __init__(self):
        self.layeredImage = True
        self.roomSize = 128
        self.headerSize = 64
        self.imageName = 'Dungeon.tiff'
        
        self.steps = [
            FillStep((13, 13, 23)),
            DrawRoomsStep(32, (77, 77, 77), (96, 0, 0)),
        ]
