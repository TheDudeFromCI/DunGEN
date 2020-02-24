from math import sqrt, floor

KEY_COLOR = (128, 96, 0)
KEY_RADIUS = 8
KEY_DASH_SIZE = 10


def draw_dotted_line(draw, start, end, length, color, width):
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


def draw_keys_layer(dungeon, draw):
    for key in dungeon.keys:
        keyRoom = key['Key Location']
        lockRoom = key['Locked Room']
        lockDoor = key['Locked Door']

        keyX = (keyRoom.pixelX + keyRoom.pixelEndX) / 2
        keyY = (keyRoom.pixelY + keyRoom.pixelEndY) / 2

        rect = (keyX - KEY_RADIUS, keyY - KEY_RADIUS,
                keyX + KEY_RADIUS, keyY + KEY_RADIUS)
        draw.ellipse(rect, fill=KEY_COLOR)

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
                         KEY_DASH_SIZE, KEY_COLOR, 3)
