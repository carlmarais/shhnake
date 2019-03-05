def drawMap(board, snakes, ourSnake):
	map = [[0 for i in range(board['height'])] for i in range(board['width'])]
	
	for snake in snakes:
		if snake['health'] == 0:
			continue

		for point in snake['body']:
			map[point['y']][point['x']] = 1

	for point in ourSnake['body']:
		map[point['y']][point['x']] = 2

	for point in board['food']:
		map[point['y']][point['x']] = 3

	prettyPrinter(map)

# Print the defined map in a tidy fashion
def prettyPrinter(map):
	divider = '|'
	for j in range(len(map[0])):
		divider += '-----|'

	print divider
	for i in range(len(map)):
		for j in range(len(map[i])):
			if j == 0:
				print '| ',
			if map[i][j] != 4:
				print map[i][j], ' | ',
			else:
				print '   | ',
		print ''
		print divider

'''
# DEBUGGING
snakes = [{'health': 5, 'body': [{'x': 0, 'y': 0}, 
								 {'x': 0, 'y': 1}, 
								 {'x': 0, 'y': 2}, 
								 {'x': 0, 'y': 3},
								 {'x': 1, 'y': 3}]},
		  {'health': 2, 'body': [{'x': 3, 'y': 5}, 
		  						 {'x': 3, 'y': 6}]},
		  {'health': 1, 'body': [{'x': 4, 'y': 7}, 
		  						 {'x': 3, 'y': 7}]}
		  						 ]
board = {'height': 8, 'width': 8, 'food': [{'x': 6, 'y': 6},{'x': 3, 'y': 3}]}
ourSnake = {'body': [{'x': 0, 'y': 7}, 
					{'x': 0, 'y': 6}]}

drawMap(board, snakes, ourSnake)
'''