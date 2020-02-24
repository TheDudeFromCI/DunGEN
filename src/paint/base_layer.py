from PIL import ImageFont

TEXT = (48, 48, 48)
FONT = ImageFont.truetype('Seagram tfb.ttf', 24)
FONT_SUB = ImageFont.truetype('Seagram tfb.ttf', 16)
ROOM_SIZE = 128
BUFFER_SIZE = 64
HEADER_SIZE = 64

BACKGROUND = (13, 13, 23)
WALLS = (77, 77, 77)
LOCKED_DOOR = (96, 0, 0)
TEXT_HEADER = (128, 128, 128)
DOOR_START = 48
DOOR_END = 48 + 32
DOOR_WIDTH = 4


def draw_hollow_rect(draw, rect, color):
    draw.rectangle(rect, fill=color)

    rect = (rect[0] + 2, rect[1] + 2, rect[2] - 2, rect[3] - 2)
    draw.rectangle(rect, fill=BACKGROUND)


def draw_base_layer(dungeon, draw):
    for room in dungeon.rooms:
        rect = (room.pixelX, room.pixelY, room.pixelEndX, room.pixelEndY)
        draw_hollow_rect(draw, rect, WALLS)

        if room.doors[0]:
            rect = (room.pixelX, room.pixelY + DOOR_START,
                    room.pixelX + DOOR_WIDTH, room.pixelY + DOOR_END)
            draw.rectangle(rect, fill=BACKGROUND)

        if room.doors[1]:
            rect = (room.pixelX + DOOR_START, room.pixelY,
                    room.pixelX + DOOR_END, room.pixelY + DOOR_WIDTH)
            draw.rectangle(rect, fill=BACKGROUND)

        if room.doors[2]:
            rect = (room.pixelEndX - DOOR_WIDTH, room.pixelY + DOOR_START,
                    room.pixelEndX, room.pixelY + DOOR_END)
            draw.rectangle(rect, fill=BACKGROUND)

        if room.doors[3]:
            rect = (room.pixelX + DOOR_START, room.pixelEndY - DOOR_WIDTH,
                    room.pixelX + DOOR_END, room.pixelEndY)
            draw.rectangle(rect, fill=BACKGROUND)

    for room in dungeon.rooms:
        if not (room.lockedDoors[0] or room.lockedDoors[1]):
            continue

        if room.lockedDoors[0]:
            rect = (room.pixelX - DOOR_WIDTH - 2, room.pixelY + DOOR_START,
                    room.pixelX + DOOR_WIDTH, room.pixelY + DOOR_END)
            draw_hollow_rect(draw, rect, LOCKED_DOOR)

        if room.lockedDoors[1]:
            rect = (room.pixelX + DOOR_START, room.pixelY - DOOR_WIDTH - 2,
                    room.pixelX + DOOR_END, room.pixelY + DOOR_WIDTH)
            draw_hollow_rect(draw, rect, LOCKED_DOOR)

    draw.text((4, 4), dungeon.name, fill=TEXT_HEADER, font=FONT)
    draw.text((4, 28), 'Dungeon ' + str(dungeon.index),
              fill=TEXT_HEADER, font=FONT_SUB)
