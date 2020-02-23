from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import sys
from dungeon_config import config
from random import randrange as rand
from random import shuffle
from math import sqrt, floor

class Dungeon:
	def __init__(self):
		self.rooms = []
		self.keys = []

	def add_room(self, room):
		self.rooms.append(room)

	def bounds(self):
		minX = minY = float("inf")
		maxX = maxY = float("-inf")

		for room in self.rooms:
			minX = min(minX, room.x)
			maxX = max(maxX, room.x)
			minY = min(minY, room.y)
			maxY = max(maxY, room.y)

		return (minX, minY, maxX, maxY)

class DungeonRoom:
	def __init__(self, type):
		self.type = type
		self.x = 0
		self.y = 0
		self.doors = [False, False, False, False]
		self.lockedDoors = [False, False, False, False]
		self.enemies = []
		self.items = []
		self.optional = False
		self.pathNext = None
		self.pathLast = None

	def count_doors(self, locked = False, excluding = []):
		doors = self.lockedDoors if locked else self.doors

		count = 0
		for i in range(4):
			if i not in excluding:
				if doors[i]:
					count += 1

		return count

	def direction_to(self, room):
		if room == None: return -1

		if room.x == self.x:
			if room.y == self.y - 1: return 1
			if room.y == self.y + 1: return 3
		if room.y == self.y:
			if room.x == self.x - 1: return 0
			if room.x == self.x + 1: return 2

		return -1

	def locked_door_dir(self, excluding = []):
		for i in range(4):
			if i not in excluding:
				if self.lockedDoors[i]: return i
		return -1

def gen_map():
	dungeon = Dungeon()

	# fill_room_count(dungeon)
	layout_rooms(dungeon)

	return dungeon

def get_entrance_room(rooms):
	entrance_name = config['Entrance']
	for room in rooms:
		if room.type['Name'] == entrance_name:
			return room

def get_room_type(name):
	for roomType in config['Room Types']:
		if roomType['Name'] == name:
			return roomType;
	
def shuffle_directions(room):
	x = room.x
	y = room.y
	directions = [(x - 1, y, 0), (x + 1, y, 2), (x, y - 1, 1), (x, y + 1, 3)]
	shuffle(directions)
	return directions

def can_place_room(dungeon, pos):
	for room in dungeon.rooms:
		if room.x == pos[0] and room.y == pos[1]:
			return False

	return True

def random_room():
	while True:
		roomType = config['Room Types'][rand(len(config['Room Types']))]

		if roomType['Name'] == config['Entrance'] or roomType['Name'] == config['Exit']:
			continue

		if roomType['Optional']:
			continue

		if roomType['Max Doors'] < 2:
			continue

		return DungeonRoom(roomType)

def create_path(dungeon, length, room, depth):
	prepareLocked = False
	keyLocation = None

	while length > 0:
		nextPos = None
		for direction in shuffle_directions(room):
			if can_place_room(dungeon, direction):
				nextPos = direction

		if nextPos is None:
			return False, None

		if depth == 0 and length == 1:
			newRoom = DungeonRoom(get_room_type(config['Exit']))
		else:
			newRoom = random_room()

		dungeon.add_room(newRoom)
		newRoom.depth = depth

		room.doors[nextPos[2]] = True
		newRoom.doors[(nextPos[2] + 2) % 4] = True

		if prepareLocked:
			prepareLocked = False

			room.lockedDoors[nextPos[2]] = True
			newRoom.lockedDoors[(nextPos[2] + 2) % 4] = True

			dungeon.keys.append(
				{'Key Location': keyLocation,
				 'Locked Room': room,
				 'Locked Door': nextPos[2]})

			keyLocation.pathNext = newRoom
			newRoom.pathLast = room
		else:
			room.pathNext = newRoom
			newRoom.pathLast = room

		newRoom.x = nextPos[0]
		newRoom.y = nextPos[1]
		room = newRoom

		length -= 1

		if length > 0:
			if rand(12) == 0:
				success, branchRoom = create_path(dungeon, 1, room, depth + 1)
				if not success:
					return False, None

				branchRoom.optional = True
			
			if depth == 0 and rand(5) == 0:
				success, branchRoom = create_path(dungeon, rand(4) + 1, room, depth + 1)
				if not success:
					return False, None

				prepareLocked = True
				keyLocation = branchRoom

	return True, room

def layout_rooms(dungeon):
	while True:
		room = DungeonRoom(get_room_type(config['Entrance']))
		dungeon.add_room(room)
		room.depth = 0

		if create_path(dungeon, rand(10, 20), room, 0):
			break

		dungeon.rooms = []

def plot_map(dungeon):
	bounds = dungeon.bounds()
	imageWidth = (bounds[2] - bounds[0] + 1) * ROOM_SIZE + BUFFER_SIZE * 2
	imageHeight = (bounds[3] - bounds[1] + 1) * ROOM_SIZE + BUFFER_SIZE * 2 + HEADER_SIZE

	for roomIndex, room in enumerate(dungeon.rooms):
		room.index = roomIndex
		room.pixelX = (room.x - bounds[0]) * ROOM_SIZE + BUFFER_SIZE
		room.pixelY = (room.y - bounds[1]) * ROOM_SIZE + BUFFER_SIZE + HEADER_SIZE

		room.pixelEndX = room.pixelX + ROOM_SIZE - 1
		room.pixelEndY = room.pixelY + ROOM_SIZE - 1

	return imageWidth, imageHeight

def draw_hollow_rect(draw, rect, color):
	draw.rectangle(rect, fill = color)

	rect = (rect[0] + 2, rect[1] + 2, rect[2] - 2, rect[3] - 2)
	draw.rectangle(rect, fill = BACKGROUND)

def draw_dotted_line(draw, start, end, length, color, width):
	delta = end[0] - start[0], end[1] - start[1]

	distance = sqrt(delta[0] ** 2 + delta[1] ** 2)
	steps = floor(distance / length / 2 + 0.5)
	vel = (delta[0] / steps / 2, delta[1] / steps / 2)

	pos = start
	for i in range(steps):
		p1 = pos[0] + vel[0], pos[1] + vel[1]
		p2 = p1[0] + vel[0], p1[1] + vel[1]
		draw.line([p1, p2], fill = color, width = width)
		pos = p2

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
def draw_base_layer(dungeon, draw):
	for room in dungeon.rooms:
		rect = (room.pixelX, room.pixelY, room.pixelEndX, room.pixelEndY)
		draw_hollow_rect(draw, rect, WALLS)

		if room.doors[0]:
			rect = (room.pixelX, room.pixelY + DOOR_START,
					room.pixelX + DOOR_WIDTH, room.pixelY + DOOR_END)
			draw.rectangle(rect, fill = BACKGROUND)

		if room.doors[1]:
			rect = (room.pixelX + DOOR_START, room.pixelY,
					room.pixelX + DOOR_END, room.pixelY + DOOR_WIDTH)
			draw.rectangle(rect, fill = BACKGROUND)

		if room.doors[2]:
			rect = (room.pixelEndX - DOOR_WIDTH, room.pixelY + DOOR_START,
					room.pixelEndX, room.pixelY + DOOR_END)
			draw.rectangle(rect, fill = BACKGROUND)

		if room.doors[3]:
			rect = (room.pixelX + DOOR_START, room.pixelEndY - DOOR_WIDTH,
					room.pixelX + DOOR_END, room.pixelEndY)
			draw.rectangle(rect, fill = BACKGROUND)

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


	draw.text((4, 4), dungeon.name, fill = TEXT_HEADER, font=FONT)
	draw.text((4, 28), 'Dungeon ' + str(dungeon.index), fill = TEXT_HEADER, font=FONT_SUB)

	img.save('dungeon.png')

	return img, draw

def draw_numbers_layer(dungeon, draw):
	for room in dungeon.rooms:
		roomName = str(room.index)

		if room.optional:
			roomName += '*'

		draw.text((room.pixelX + 4, room.pixelY + 2), roomName, fill = TEXT, font=FONT)

KEY_COLOR = (128, 96, 0)
KEY_RADIUS = 8
KEY_DASH_SIZE = 10
def draw_keys_layer(dungeon, draw):
	for key in dungeon.keys:
		keyRoom = key['Key Location']
		lockRoom = key['Locked Room']
		lockDoor = key['Locked Door']

		keyX = (keyRoom.pixelX + keyRoom.pixelEndX) / 2
		keyY = (keyRoom.pixelY + keyRoom.pixelEndY) / 2

		rect = (keyX - KEY_RADIUS, keyY - KEY_RADIUS, keyX + KEY_RADIUS, keyY + KEY_RADIUS)
		draw.ellipse(rect, fill = KEY_COLOR)

		if lockDoor == 0:   lockX = lockRoom.pixelX
		elif lockDoor == 2: lockX = lockRoom.pixelEndX
		else:               lockX = (lockRoom.pixelX + lockRoom.pixelEndX) / 2

		if lockDoor == 1:   lockY = lockRoom.pixelY
		elif lockDoor == 3: lockY = lockRoom.pixelEndY
		else:               lockY = (lockRoom.pixelY + lockRoom.pixelEndY) / 2

		draw_dotted_line(draw, (lockX, lockY), (keyX, keyY), KEY_DASH_SIZE, KEY_COLOR, 3)

PATH_COLOR = (76, 76, 0)
PATH_DASH_SIZE = 7
PATH_BACKTRACK_OFFSET = 8

def path_draw_branch(dungeon, draw, room, next, d, path, excluding):
	nextD = next.direction_to(next.pathNext)
	lockD = next.locked_door_dir(excluding = excluding)

	if nextD == d:
		clockwise = (lockD + 1) % 4 != d
	else:
		clockwise = (nextD + 3) % 4 != d

	offset = -PATH_BACKTRACK_OFFSET if clockwise else PATH_BACKTRACK_OFFSET
	p2 = ((next.pixelX + next.pixelEndX) / 2, (next.pixelY + next.pixelEndY) / 2)
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

		mainC = ((branch.pixelX + branch.pixelEndX) / 2, (branch.pixelY + branch.pixelEndY) / 2)

		if not backward and branch.depth != branch.pathNext.depth:
			n = branch.pathLast
			lockedRoom = branch.pathNext

			cx = cy = 0
			if lastD % 2 == 0: cy = sideY
			if lastD % 2 == 1: cx = sideX

			c = mainC
			if cx == -1: c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
			if cx ==  1: c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
			if cy == -1: c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
			if cy ==  1: c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
			path.append(c)

			if lastD % 2 == 0: cy = -sideY
			if lastD % 2 == 1: cx = -sideX

			c = mainC
			if cx == -1: c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
			if cx ==  1: c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
			if cy == -1: c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
			if cy ==  1: c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
			path.append(c)

			if lastD == 0: cx = -1
			if lastD == 1: cy = -1
			if lastD == 2: cx = 1
			if lastD == 3: cy = 1

			backward = True
			lastD = nextD

			if n == room:
				path_finish_branch(dungeon, draw, branch, lockD, path, mainC, n, lastD, sideX, sideY)

		elif backward and branch.pathLast == room:
			n = room
			path_finish_branch(dungeon, draw, branch, lockD, path, mainC, n, lastD, sideX, sideY)
		else:
			n = branch.pathLast if backward else branch.pathNext
			nextD = branch.direction_to(n)

			s = sideY if lastD % 2 == 0 else sideX

			if lastD % 2 == 0: cy = s
			if lastD % 2 == 1: cx = s

			if lastD == 0:
				if nextD == 1: cx = s
				if nextD == 2: cx = 1
				if nextD == 3: cx = -s
			if lastD == 1:
				if nextD == 0: cy = s
				if nextD == 2: cy = -s
				if nextD == 3: cy = 1
			if lastD == 2:
				if nextD == 0: cx = -1
				if nextD == 1: cx = -s
				if nextD == 3: cx = s
			if lastD == 3:
				if nextD == 0: cy = -s
				if nextD == 1: cy = -1
				if nextD == 2: cy = s
		
			c = mainC
			if cx == -1: c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
			if cx ==  1: c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
			if cy == -1: c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
			if cy ==  1: c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
			path.append(c)

			lastD = (nextD + 2) % 4

		branch = n
		sideX = cx
		sideY = cy
	return lockedRoom

def path_finish_branch(dungeon, draw, branch, lockD, path, mainC, n, lastD, sideX, sideY):
	nextD = branch.direction_to(n)

	s = sideY if lastD % 2 == 0 else sideX

	if lastD % 2 == 0: cy = s
	if lastD % 2 == 1: cx = s

	if lastD == 0:
		if nextD == 1: cx = s
		if nextD == 2: cx = 1
		if nextD == 3: cx = -s
	if lastD == 1:
		if nextD == 0: cy = s
		if nextD == 2: cy = -s
		if nextD == 3: cy = 1
	if lastD == 2:
		if nextD == 0: cx = -1
		if nextD == 1: cx = -s
		if nextD == 3: cx = s
	if lastD == 3:
		if nextD == 0: cy = -s
		if nextD == 1: cy = -1
		if nextD == 2: cy = s

	if (lastD + 2) % 4 == lockD:
		if lockD == 0: cx = -1
		if lockD == 1: cy = -1
		if lockD == 2: cx = 1
		if lockD == 3: cy = 1

		c = mainC
		if cx == -1: c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
		if cx ==  1: c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
		if cy == -1: c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
		if cy ==  1: c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
		path.append(c)

		if lockD % 2 == 0: cy = 0
		if lockD % 2 == 1: cx = 0
	else:
		if lockD % 2 == 0: cy = 0
		if lockD % 2 == 1: cx = 0

	c = mainC
	if cx == -1: c = (c[0] - PATH_BACKTRACK_OFFSET, c[1])
	if cx ==  1: c = (c[0] + PATH_BACKTRACK_OFFSET, c[1])
	if cy == -1: c = (c[0], c[1] - PATH_BACKTRACK_OFFSET)
	if cy ==  1: c = (c[0], c[1] + PATH_BACKTRACK_OFFSET)
	path.append(c)

def draw_path_layer(dungeon, draw):
	room = dungeon.rooms[0]
	path = [((room.pixelX + room.pixelEndX) / 2, (room.pixelY + room.pixelEndY) / 2)]

	next = room.pathNext
	lastD = None
	while room != None:
		if next == None:
			break

		d = room.direction_to(next)

		if d == -1:
			break

		excluding = [(d + 2) % 4]
		if next.count_doors(locked = True, excluding = excluding) > 0:
			lockedRoom = path_draw_branch(dungeon, draw, room, next, d, path, excluding)
			room = next
			next = lockedRoom
		else:
			path.append(((next.pixelX + next.pixelEndX) / 2, (next.pixelY + next.pixelEndY) / 2))
			room = next
			next = next.pathNext
			lastD = d
	
	draw.line(path, fill = PATH_COLOR, width = 2)

			
def open_image(filename):
	open_cmd = 'open'
	if sys.platform.startswith('linux'):
		open_cmd = 'xdg-open'
	if sys.platform.startswith('win32'):
		open_cmd = 'start'

	filename = os.getcwd() + os.path.sep + filename
	subprocess.run([open_cmd, filename], check=True)

if __name__ == '__main__':
	dungeon = gen_map()
	dungeon.name = 'The Sewers'
	dungeon.index = 2

	imageWidth, imageHeight = plot_map(dungeon)

	img = Image.new('RGB', (imageWidth, imageHeight), color = BACKGROUND)
	layer2 = Image.new('RGBA', (imageWidth, imageHeight), color = None)
	layer3 = Image.new('RGBA', (imageWidth, imageHeight), color = None)
	layer4 = Image.new('RGBA', (imageWidth, imageHeight), color = None)

	#layer2 = layer3 = layer4 = img

	draw_base_layer(dungeon, ImageDraw.Draw(img))
	draw_numbers_layer(dungeon, ImageDraw.Draw(layer2))
	draw_keys_layer(dungeon, ImageDraw.Draw(layer3))
	draw_path_layer(dungeon, ImageDraw.Draw(layer4))

	img.save('dungeon.tiff', save_all = True, append_images = [
		layer2, layer3, layer4])
	#open_image('dungeon.tiff')

