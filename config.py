config = {
	'Entrance': 'Entrance Room',
	'Exit': 'Boss Room',

	'Room Types':
	[
		{
			'Name': 'Boss Room',

			'Enemy Count': [1, 1],

			'Room Count': [1, 1],
			'Priority': 1,
			'Optional': False,

			'Max Doors': 1,
			'Can Contain Key': False,

			'Variations': ['Tank Type', 'Minion Controller', 'Bullet-O-Matic'],


			'Possible Items Finds': [],
			'Chance Of Item': 0,
			'Number Of Items': [1, 1],
		},

		{
			'Name': 'Mini-Boss Room',

			'Enemy Count': [1, 1],

			'Room Count': [0, 3],
			'Priority': 2,
			'Optional': False,

			'Max Doors': 2,
			'Can Contain Key': True,

			'Variations': ['Tank Type', 'Minion Controller', 'Time Survival', 'Bullet-O-Matic'],

			'Possible Items Finds': [],
			'Chance Of Item': 0,
			'Number Of Items': [1, 1],
		},

		{
			'Name': 'Entrance Room',

			'Enemy Count': [0, 0],

			'Room Count': [1, 1],
			'Priority': 1,
			'Optional': False,

			'Max Doors': 3,
			'Can Contain Key': False,

			'Variations': [],

			'Possible Items Finds': ['Heart', 'Half Heart', 'Silver Charge Pack'],
			'Chance Of Item': 1 / 3,
			'Number Of Items': [1, 1],
		},

		{
			'Name': 'Common Room',

			'Enemy Count': [0, 5],

			'Room Count': [0, 20],
			'Priority': 5,
			'Optional': False,

			'Max Doors': 4,
			'Can Contain Key': True,

			'Variations': ['Empty', 'Hallway', 'Simple Maze', 'Complex Maze'],

			'Possible Items Finds': ['Heart', 'Half Heart', 'Silver Charge Pack'],
			'Chance Of Item': 1 / 5,
			'Number Of Items': [1, 1],
		},

		{
			'Name': 'Secret Room',

			'Enemy Count': [0, 0],

			'Room Count': [3, 8],
			'Priority': 3,
			'Optional': True,

			'Max Doors': 1,
			'Can Contain Key': False,

			'Variations': ['Open By Level', 'Open By Detonator', 'Open By Kill Enemy'],

			'Possible Items Finds': ['Gold Charge Pack', 'Extra Life'],
			'Chance Of Item': 1 / 1,
			'Number Of Items': [1, 3],
		},
	],
}
