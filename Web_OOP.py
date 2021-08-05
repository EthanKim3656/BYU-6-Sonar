import random
import sys
import math

class Board:
	board = []
	chests = []
	previousMoves = []

	def createBoard(self):
		self.board = []
		self.previousMoves = []
		for x in range(60):  # The main list is a list of 60 lists.
			self.board.append([])
			for y in range(15):  # Each list in the main list has 15 single-character strings.
				# Use different characters for the ocean to make it more readable.
				if random.randint(0, 1) == 0:
					self.board[x].append('~')
				else:
					self.board[x].append('`')

	def getBoard(self):
		return self.board

	def generateRandomChests(self, numChests):
		# Create a list of chest data structures (two-item lists of x, y int coordinates).
		self.chests = [[10,0],[0,5],[20,0]]
		#self.chests = []
		#while len(self.chests) < numChests:
		#	newChest = [random.randint(0, 59), random.randint(0, 14)]
		#	if newChest not in self.chests:  # Make sure a chest is not already here.
		#		self.chests.append(newChest)

	def makeMove(self, x, y):
		# Change the board data structure with a sonar device character. Remove treasure chests from the chests list
		# as they are found. Return False if this is an invalid move. Otherwise, return the string of the result of
		# this move.
		if [x,y] not in self.previousMoves:
			self.previousMoves.append([x, y])
		smallestDistance = 100  # Any chest will be closer than 100.
		for cx, cy in self.chests:
			distance = math.sqrt((cx - x) * (cx - x) + (cy - y) * (cy - y))

			if distance < smallestDistance:  # We want the closest treasure chest.
				smallestDistance = distance

		smallestDistance = round(smallestDistance)

		if smallestDistance == 0:
			# xy is directly on a treasure chest!
			self.chests.remove([x, y])
			for x, y in self.previousMoves:
					self.makeMove(x, y)
			return 'You have found a sunken treasure chest!'
		elif smallestDistance < 10:
			self.board[x][y] = str(smallestDistance)
			return f'Treasure detected at a distance of {smallestDistance} from the sonar device.'
		else:
			self.board[x][y] = 'X'
			return 'Sonar did not detect anything. All treasure chests out of range.'

	def validateMove(self, x, y):
		if not (0 <= x <= 59 and 0 <= y <= 14):
			return False, 'Out of bounds'
		elif [x, y] in self.previousMoves:
			return False, 'You have already moved there.'
		else:
			return True, ''




class UI:

	def initialize(self):
		return('''<head><link href="index.css"rel="stylesheet"/></head><form action='/game'>Would you like to see the instructions?<br><input type='text' name='instr'></form>''')
		

	def printer(self, board, message):
		boardString = f'''<head><link href="index.css" rel="stylesheet"/></head>{message}'''
		# Draw the board data structure.
		tensDigitsLine = '    '  # Initial space for the numbers down the left side of the board
		for i in range(1, 6):
			tensDigitsLine += (' ' * 9) + str(i)

		# Print the numbers across the top of the board.
		boardString +=('<br>'+tensDigitsLine)
		boardString +=('<br>   ' + ('0123456789' * 6)+ '<br>')
		

		# Print each of the 15 rows.
		for row in range(15):
			# Single-digit numbers need to be padded with an extra space.
			if row < 10:
				extraSpace = ' '
			else:
				extraSpace = ''

			# Create the string for this row on the board.
			boardRow = ''
			for column in range(60):
				boardRow += board.getBoard()[column][row]

			boardString+=(f'{extraSpace} {row}{boardRow} {row}<br>')

		# Print the numbers across the bottom of the board.
		boardString +=('   ' + ('0123456789' * 6) + '<br>')
		boardString +=(tensDigitsLine)
		boardString += '''<br>Where do you want to drop the next sonar device? (0-59 0-14)'''
		boardString += '''<form action='/game'>X:<input type='text' name='x'> Y:<input type='text' name='y'> <input type="submit"></form>'''
		return boardString

	def enterPlayerMove(self, x, y, board):
		# Let the player enter their move. Return a two-item list of int xy coordinates.
		valid = False
		if x.isdigit() and y.isdigit():
			x = int(x)
			y = int(y)
			valid, message = board.validateMove(x, y)
			if valid:
				return valid, board.makeMove(x, y)
			else:
				return valid, (message)
		else:
			return valid, 'You did not input numbers'

	def showInstructions(self):
		return('''<head><link href="index.css" rel="stylesheet"/></head>Instructions:
You are the captain of a treasure-hunting ship.Your current mission is to use sonar devices to find sunken treasure chests at the bottom of the ocean. However a rival is also searching for the chests. Both of you have cheap sonar that only finds distance, not direction. Enter the coordinates to drop a sonar device. The ocean map will be marked with how far away the nearest chest is, or an X if it is beyond the sonar device's range.For example, the C marks are where chests are. The sonar device shows a 3 because the closest chest is 3 spaces away.

          1         2         3
  012345678901234567890123456789012
0 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 0
1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 1
2 ~~~C~~3~~~~~~C~~~~~~~~~~~~~~~~~~~ 2
3 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 3
4 ~~~~~~~~~~~~~C~~~~~~~~~~~~~~~~~~~ 4
  012345678901234567890123456789012
          1         2         3

(In the real game, the chests are not visible in the ocean.)
When you drop a sonar device directly on a chest, you retrieve it and the other sonar devices update to show how far away the next nearest chest is. The chests are beyond the range of the sonar device on the left, so it shows an X.
          1         2         3
  012345678901234567890123456789012
0 ~~~~`~```~`~``~~~``~`~~``~~~``~`~ 0
1 ~`~`~``~~`~```~~~```~~`~`~~~`~~~~ 1
2 `~`X``7`~~~~`C`~~~~`````~~``~~~`` 2
3 ````````~~~`````~~~`~`````~`~``~` 3
4 ~`~~~~`~~`~~`C`~``~~`~~~`~```~``~ 4
  012345678901234567890123456789012
          1         2         3

<a href='/game?instr=no'>Go to game</a>
''')


def container():

	while True:
		# Game setup
		ui = UI()
		board = Board()
		board.generateRandomChests(3)
		board.createBoard()

		ui.initialize()
		ui.printer(board)

		sonarDevices = 20

		while sonarDevices > 0:
			# Show sonar device and chest statuses.
			print(f'You have {sonarDevices} sonar device(s) left. {len(board.chests)} treasure chest(s) remaining.')

			moveResult = ui.enterPlayerMove(board)
			if moveResult == 'You have found a sunken treasure chest!':
				# Update all the sonar devices currently on the map.
				for x, y in board.previousMoves:
					board.makeMove(x, y)
			ui.printer(board)
			print(moveResult)

			if len(board.chests) == 0:
				print('You have found all the sunken treasure chests! Congratulations and good game!')
				break

			sonarDevices -= 1

		if sonarDevices == 0:
			print('We\'ve run out of sonar devices! Now we have to turn the ship around and head')
			print('for home with treasure chests still out there! Game over.')
			print('The remaining chests were here:')
			for x, y in board.chests:
				print(f' {x}, {y}')

		print('Do you want to play again? (yes or no)')
		if not input().lower().startswith('y'):
			sys.exit()


