from PIL import ImageFont

TEXT = (48, 48, 48)
FONT = ImageFont.truetype('Seagram tfb.ttf', 24)


def draw_numbers_layer(dungeon, draw):
    for room in dungeon.rooms:
        roomName = str(room.index)

        if room.optional:
            roomName += '*'

        draw.text((room.pixelX + 4, room.pixelY + 2),
                  roomName, fill=TEXT, font=FONT)
