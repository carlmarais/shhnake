# Battlesnake 2019: shhnake
#
# CREATORS: - Cameron Day
#			- Carl Marais
#
# PURPOSES: - Be snake.
#			- Survive.
#			- Kill other snakes.
#			- Be the very best - the best there ever was.

import json
import os
import random
import bottle
import operator

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
	return '''Battlesnake documentation can be found at <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.\n\nShhnake is running successfully.'''

@bottle.route('/static/<path:path>')
def static(path):
	"""
	Given a path, return the static file located relative
	to the static folder.

	This can be used to return the snake head URL in an API response.
	"""
	return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
	"""
	A keep-alive endpoint used to prevent cloud application platforms,
	such as Heroku, from sleeping the application instance.
	"""
	return ping_response()

@bottle.post('/start')
def start():
	data = bottle.request.json

	#print(json.dumps(data))
	
	color = '#42d1ab'
	headType = 'evil'
	tailType = 'bolt'

	return start_response(color, headType, tailType)


@bottle.post('/move')
def move():
	data = bottle.request.json

	#print(json.dumps(data))

	ourSnake = data['you']
	ourHead = ourSnake['body'][0]
	ourTail = ourSnake['body'][-1]

	otherSnakes = []

	for snake in data['board']['snakes']:
		otherSnakes.append(snake)

	foodList = data['board']['food']

	# Eliminate dangerous moves.
	directions = ['up', 'down', 'left', 'right']
	directions = checkWall(data, directions, ourHead['x'], ourHead['y'])
	print "Directions after checkWall: " + str(directions)
	directions = checkSelf(data, directions, ourHead['x'], ourHead['y'], ourSnake)
	print "Directions after checkSelf: " + str(directions)
	directions = tailAvoidance(data, directions, otherSnakes, ourHead, ourTail)
	print "Directions after tailAvoidance: " + str(directions)
	directions = checkHeadCollision(data, directions, ourHead, ourSnake, otherSnakes)
	print "Directions after checkHeadCollision: " + str(directions)

	# If snake's health is below designated threshold, seek food. Else, pick random direction.

	snake_lengths = [len(snake['body']) for snake in otherSnakes]

	if ourSnake['health'] <= 1.7*(data['board']['width'] + data['board']['height']) or len(ourSnake['body']) <= min(snake_lengths) - 2:
		direction = findFood(data, directions, ourHead, foodList)
	else:
		direction = bfs_line(data, directions, ourHead, ourTail, ourSnake, otherSnakes, 3)
		# direction = random.choice(directions)

	# For debugging purposes.
	print "Final return is: "
	print direction

	return move_response(str(random.choice(direction)))

def checkWall(data, directions, our_head_x, our_head_y):
	# Remove directions that result in snake running into walls.

	head_x = our_head_x
	head_y = our_head_y

	# X Directions
	if 'right' in directions and head_x == (data['board']['width'] - 1):
		directions.remove('right')
	elif 'left' in directions and head_x == 0:
		directions.remove('left')

	# Y Directions
	if 'down' in directions and head_y == (data['board']['height'] - 1):
		directions.remove('down')
	elif 'up' in directions and head_y == 0:
		directions.remove('up')

	return directions

def checkSelf(data, directions, our_head_x, our_head_y, ourSnake):
	# Remove directions that result in snake running into self.

	head_x = our_head_x
	head_y = our_head_y

	for i in range(len(data['you']['body'])):
		body_x = ourSnake['body'][i]['x']
		body_y = ourSnake['body'][i]['y']

		if 'right' in directions and head_x + 1 == body_x and head_y == body_y:
			directions.remove('right')
		elif 'left' in directions and head_x - 1 == body_x and head_y == body_y:
			directions.remove('left')
		elif 'down' in directions and head_y + 1 == body_y and head_x == body_x:
			directions.remove('down')
		elif 'up' in directions and head_y - 1 == body_y and head_x == body_x:
			directions.remove('up')

	return directions

def findFood(data, directions, ourHead, foodList):
	# Remove directions that result in snake taking longer to reach nearest food.
	# Consider |head_x - food_x| + |head_y - food_y|

	if len(foodList) == 0:
		return directions

	min_dist = 10000

	head_x = ourHead['x']
	head_y = ourHead['y']

	for i in range(len(foodList)):

		food_i_x = foodList[i]['x']
		food_i_y = foodList[i]['y']

		dist_food_i = abs(head_x - food_i_x) + abs(head_y - food_i_y)

		if dist_food_i <= min_dist:

			min_dist = dist_food_i

			closest_food = i
			closest_food_x = food_i_x
			closest_food_y = food_i_y

	choices = {key: None for key in directions}

	if 'left' in directions:
		choices['left'] = abs(head_x - closest_food_x - 1) + abs(head_y - closest_food_y)
	if 'right' in directions:
		choices['right'] = abs(head_x - closest_food_x + 1) + abs(head_y - closest_food_y)
	if 'up' in directions:
		choices['up'] = abs(head_x - closest_food_x - 1) + abs(head_y - closest_food_y - 1)
	if 'down' in directions:
		choices['down'] = abs(head_x - closest_food_x - 1) + abs(head_y - closest_food_y + 1)

	return [min(choices, key=choices.get)]

def tailAvoidance(data, directions, otherSnakes, ourHead, ourTail):
	# Avoid collisions with other snake bodies.

	head_x = ourHead['x']
	head_y = ourHead['y']

	for snake in otherSnakes:
		if snake['health'] == 0:
			continue
		else:
			for i in range(1, len(snake['body'])):
				snake_i_x = snake['body'][i]['x']
				snake_i_y = snake['body'][i]['y']

				if 'down' in directions:
					if snake_i_x == head_x and snake_i_y == head_y + 1:
						directions.remove('down')
				if 'up' in directions:
					if snake_i_x == head_x and snake_i_y == head_y - 1:
						directions.remove('up')
				if 'right' in directions:
					if snake_i_y == head_y and snake_i_x == head_x + 1:
						directions.remove('right')
				if 'left' in directions:
					if snake_i_y == head_y and snake_i_x == head_x - 1:
						directions.remove('left')

	return directions

def checkHeadCollision(data, directions, ourHead, ourSnake, otherSnakes):
	# Avoid a head to head collision if we are <= the other snake's size

	if len(directions) == 1:
		return directions

	our_head_x = ourHead['x']
	our_head_y = ourHead['y']

	counts = {
		'up': 0,
		'down': 0,
		'left': 0,
		'right': 0,
	}

	for snake in otherSnakes:

		if snake['health'] == 0:
			continue

		snake_head_x = snake['body'][0]['x']
		snake_head_y = snake['body'][0]['y']

		# Up Direction
		if 'up' in directions:
			if our_head_x == snake_head_x and (our_head_y - snake_head_y == 1):
				directions.remove('up')
			elif our_head_x == snake_head_x and (our_head_y - snake_head_y == 2):
				counts['up'] += 1
		# Down Direction
		if 'down' in directions:
			if our_head_x == snake_head_x and (our_head_y - snake_head_y == -1):
				directions.remove('down')
			elif our_head_x == snake_head_x and (our_head_y - snake_head_y == -2):
				counts['down'] += 1
		# Left Direction
		if 'left' in directions:
			if our_head_y == snake_head_y and (our_head_x - snake_head_x == 1):
				directions.remove('left')
			elif our_head_y == snake_head_y and (our_head_x - snake_head_x == 2):
				counts['left'] += 1
		# Right Direction
		if 'right' in directions:
			if our_head_y == snake_head_y and (our_head_x - snake_head_x == -1):
				directions.remove('right')
			elif our_head_y == snake_head_y and (our_head_x - snake_head_x == -2):
				counts['right'] += 1

		if len(ourSnake['body']) > len(snake['body']):
			continue

		# Up/Right Direction
		if 'right' in directions or 'up' in directions:
			if (our_head_x - snake_head_x == -1) and (our_head_y - snake_head_y == 1):
				counts['up'] += 1
				counts['right'] += 1
		# Up/Left Direction
		if 'left' in directions or 'up' in directions:
			if (our_head_x - snake_head_x == 1) and (our_head_y - snake_head_y == 1):
				counts['up'] += 1
				counts['left'] += 1
		# Down/Right Direction
		if 'right' in directions or 'down' in directions:
			if (our_head_x - snake_head_x == -1) and (our_head_y - snake_head_y == -1):
				counts['down'] += 1
				counts['right'] += 1
		# Down/Left Direction
		if 'left' in directions or 'down' in directions:
			if (our_head_x - snake_head_x == 1) and (our_head_y - snake_head_y == -1):
				counts['down'] += 1
				counts['left'] += 1

		remove_dir = max(counts, key=counts.get)
		if remove_dir in directions and counts[remove_dir] > 0:
			directions.remove(remove_dir)

		if len(directions) >= 2:
			counts[remove_dir] = 0
			remove_dir = max(counts, key=counts.get)
			if remove_dir in directions and counts[remove_dir] > 0:
				directions.remove(remove_dir)

	return directions

def bfs_line(data, remainingDirs, ourHead, ourTail, ourSnake, otherSnakes, depth):

	# remainingDirs is an array of directions e.g. ['down', 'up']

	dirCounter = {
		'up': 0,
		'down': 0,
		'left': 0,
		'right': 0
	}
	tempHead = {
		'x': -1,
		'y': -1
	}
	tempDirections = []

	for dir in remainingDirs:
		currDirection = True
		tempHead = get_temp_head(ourHead, dir)
		depthCounter = 0

		print "tempHead is: "
		print tempHead['x']

		while currDirection and depthCounter < depth:
			# Eliminate dangerous moves.
			tempDirections.append(dir)
			tempDirections = checkWall(data, tempDirections, tempHead['x'], tempHead['y'])
			# print "Directions after checkWall: " + str(directions)
			tempDirections = checkSelf(data, tempDirections, tempHead['x'], tempHead['y'], ourSnake)
			# print "Directions after checkSelf: " + str(directions)
			tempDirections = tailAvoidance(data, tempDirections, otherSnakes, tempHead, ourTail)
			# print "Directions after tailAvoidance: " + str(directions)
			tempDirections = checkHeadCollision(data, tempDirections, tempHead, ourSnake, otherSnakes)
			# print "Directions after checkHeadCollision: " + str(directions)

			depthCounter += 1

			if dir in tempDirections:
				dirCounter[dir] += 1
				tempHead = get_temp_head(tempHead, dir)
			else:
				currDirection = False

	maxDir = max(dirCounter.iteritems(), key=operator.itemgetter(1))[0]
	print "The max direction is: "
	print dirCounter
	print maxDir
	if dirCounter[maxDir] > 0:
		return [maxDir]
	else:
		return remainingDirs


def get_temp_head(ourHead, direction):
	tempHead = {
		'x': -1,
		'y': -1
	}
	tempHead['x'] = ourHead['x']
	tempHead['y'] = ourHead['y']
	if direction == 'left':
		tempHead['x'] -= 1
		return tempHead
	elif direction == 'right':
		tempHead['x'] += 1
		return tempHead
	elif direction == 'up':
		tempHead['y'] -= 1
		return tempHead
	elif direction == 'down':
		tempHead['y'] += 1
		return tempHead


@bottle.post('/end')
def end():
	data = bottle.request.json

	"""
	TODO: If your snake AI was stateful,
		clean up any stateful objects here.
	"""
	#print(json.dumps(data))

	return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
	bottle.run(
		application,
		host=os.getenv('IP', '0.0.0.0'),
		port=os.getenv('PORT', '8080'),
		debug=os.getenv('DEBUG', True)
	)
