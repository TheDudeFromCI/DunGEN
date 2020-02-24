PATH_COLOR = (76, 76, 0)
PATH_DASH_SIZE = 7
PATH_BACKTRACK_OFFSET = 8


def path_draw_branch(dungeon, draw, room, next, d, path, excluding):
    nextD = next.direction_to(next.pathNext)
    lockD = next.locked_door_dir(excluding=excluding)

    if nextD == d:
        clockwise = (lockD + 1) % 4 != d
    else:
        clockwise = (nextD + 3) % 4 != d

    offset = -PATH_BACKTRACK_OFFSET if clockwise else PATH_BACKTRACK_OFFSET
    p2 = ((next.pixelX + next.pixelEndX) / 2,
          (next.pixelY + next.pixelEndY) / 2)
    if d == 0:
        p2 = (p2[0] + PATH_BACKTRACK_OFFSET, p2[1])
        p3 = (p2[0], p2[1] - offset)
        sideX = 1
        sideY = 1 if clockwise else -1
    if d == 1:
        p2 = (p2[0], p2[1] + PATH_BACKTRACK_OFFSET)
        p3 = (p2[0] + offset, p2[1])
        sideX = -1 if clockwise else 1
        sideY = 1
    if d == 2:
        p2 = (p2[0] - PATH_BACKTRACK_OFFSET, p2[1])
        p3 = (p2[0], p2[1] + offset)
        sideX = -1
        sideY = -1 if clockwise else 1
    if d == 3:
        p2 = (p2[0], p2[1] - PATH_BACKTRACK_OFFSET)
        p3 = (p2[0] - offset, p2[1])
        sideX = 1 if clockwise else -1
        sideY = -1

    path.append(p2)
    path.append(p3)

    p = p3
    branch = next.pathNext
    lastD = (next.direction_to(branch) + 2) % 4
    backward = False

    lockedRoom = None

    while branch != room:

        mainC = ((branch.pixelX + branch.pixelEndX) / 2,
                 (branch.pixelY + branch.pixelEndY) / 2)

        if not backward and branch.depth != branch.pathNext.depth:
            n = branch.pathLast
            lockedRoom = branch.pathNext

            cx = cy = 0
            if lastD % 2 == 0:
                cy = sideY
            if lastD % 2 == 1:
                cx = sideX

            c = mainC
            if cx == -1:
                c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
            if cx == 1:
                c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
            if cy == -1:
                c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
            if cy == 1:
                c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
            path.append(c)

            if lastD % 2 == 0:
                cy = -sideY
            if lastD % 2 == 1:
                cx = -sideX

            c = mainC
            if cx == -1:
                c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
            if cx == 1:
                c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
            if cy == -1:
                c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
            if cy == 1:
                c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
            path.append(c)

            if lastD == 0:
                cx = -1
            if lastD == 1:
                cy = -1
            if lastD == 2:
                cx = 1
            if lastD == 3:
                cy = 1

            backward = True
            lastD = nextD

            if n == room:
                path_finish_branch(dungeon, draw, branch,
                                   lockD, path, mainC, n, lastD, sideX, sideY)

        elif backward and branch.pathLast == room:
            n = room
            path_finish_branch(dungeon, draw, branch, lockD,
                               path, mainC, n, lastD, sideX, sideY)
        else:
            n = branch.pathLast if backward else branch.pathNext
            nextD = branch.direction_to(n)

            s = sideY if lastD % 2 == 0 else sideX

            if lastD % 2 == 0:
                cy = s
            if lastD % 2 == 1:
                cx = s

            if lastD == 0:
                if nextD == 1:
                    cx = s
                if nextD == 2:
                    cx = 1
                if nextD == 3:
                    cx = -s
            if lastD == 1:
                if nextD == 0:
                    cy = s
                if nextD == 2:
                    cy = -s
                if nextD == 3:
                    cy = 1
            if lastD == 2:
                if nextD == 0:
                    cx = -1
                if nextD == 1:
                    cx = -s
                if nextD == 3:
                    cx = s
            if lastD == 3:
                if nextD == 0:
                    cy = -s
                if nextD == 1:
                    cy = -1
                if nextD == 2:
                    cy = s

            c = mainC
            if cx == -1:
                c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
            if cx == 1:
                c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
            if cy == -1:
                c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
            if cy == 1:
                c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
            path.append(c)

            lastD = (nextD + 2) % 4

        branch = n
        sideX = cx
        sideY = cy
    return lockedRoom


def path_finish_branch(dungeon, draw, branch, lockD, path, mainC, n, lastD, sideX, sideY):
    nextD = branch.direction_to(n)

    s = sideY if lastD % 2 == 0 else sideX

    if lastD % 2 == 0:
        cy = s
    if lastD % 2 == 1:
        cx = s

    if lastD == 0:
        if nextD == 1:
            cx = s
        if nextD == 2:
            cx = 1
        if nextD == 3:
            cx = -s
    if lastD == 1:
        if nextD == 0:
            cy = s
        if nextD == 2:
            cy = -s
        if nextD == 3:
            cy = 1
    if lastD == 2:
        if nextD == 0:
            cx = -1
        if nextD == 1:
            cx = -s
        if nextD == 3:
            cx = s
    if lastD == 3:
        if nextD == 0:
            cy = -s
        if nextD == 1:
            cy = -1
        if nextD == 2:
            cy = s

    if (lastD + 2) % 4 == lockD:
        if lockD == 0:
            cx = -1
        if lockD == 1:
            cy = -1
        if lockD == 2:
            cx = 1
        if lockD == 3:
            cy = 1

        c = mainC
        if cx == -1:
            c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
        if cx == 1:
            c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
        if cy == -1:
            c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
        if cy == 1:
            c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
        path.append(c)

        if lockD % 2 == 0:
            cy = 0
        if lockD % 2 == 1:
            cx = 0
    else:
        if lockD % 2 == 0:
            cy = 0
        if lockD % 2 == 1:
            cx = 0

    c = mainC
    if cx == -1:
        c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
    if cx == 1:
        c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
    if cy == -1:
        c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
    if cy == 1:
        c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
    path.append(c)


def draw_path_layer(dungeon, draw):
    room = dungeon.rooms[0]
    path = [((room.pixelX + room.pixelEndX) / 2,
             (room.pixelY + room.pixelEndY) / 2)]

    next = room.pathNext
    lastD = None
    while room != None:
        if next == None:
            break

        d = room.direction_to(next)

        if d == -1:
            break

        excluding = [(d + 2) % 4]
        if next.count_doors(locked=True, excluding=excluding) > 0:
            lockedRoom = path_draw_branch(
                dungeon, draw, room, next, d, path, excluding)
            room = next
            next = lockedRoom
        else:
            path.append(((next.pixelX + next.pixelEndX) / 2,
                         (next.pixelY + next.pixelEndY) / 2))
            room = next
            next = next.pathNext
            lastD = d

    draw.line(path, fill=PATH_COLOR, width=2)
