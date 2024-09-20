from flask import render_template, make_response, redirect, url_for, request
from flask_restful import Resource
from flask_socketio import Namespace, emit
from tic_tac_toe import redis_ob
import random
import json
from string import ascii_uppercase

# List to hold room codes
rooms = []


# Function to generate a unique room code
def generate_room_code():
	while True:
		code = ""
		# Generate a 5-letter code using uppercase letters
		for _ in range(5):
			code += random.choice(ascii_uppercase)
		# Ensure the code is unique
		if code not in rooms:
			rooms.append(code)  # Add to rooms if unique
			break
	return code


# Resource for the home page
class Home(Resource):

	def get(self):
		# Render the home template
		return make_response(render_template('home.html'))

	def post(self):
		name = request.form.get('name')  # Get the username from the form
		room_code = request.form.get('room_code')  # Get the room code
		join = request.form.get('join', False)  # Check if user wants to join a room
		create = request.form.get('create', False)  # Check if user wants to create a room

		if join is False:
			# If not joining, create a new room
			new_room_code = generate_room_code()
			return redirect(url_for('game', room_code=new_room_code, username=name, player=1))

		# If creating a room, but no room code is provided
		if create is False and room_code == '':
			return make_response(render_template('home.html', error=True, username=name))
		else:
			try:
				# Try to remove the room code if it exists (indicates joining)
				rooms.remove(room_code)
				return redirect(url_for('game', room_code=room_code, username=name, player=2))
			except:
				# If room code does not exist, show error
				return make_response(render_template('home.html', error_max=True, username=name))


# Resource for the game page
class Game(Resource):
	def get(self, room_code, username, player):
		# Render the game template with room code and player information
		return make_response(render_template('game.html', room_code=room_code, username=username, player=player))


# Set the square numbers for a user in Redis
def set_square_numbers(user, square_numbers):
	redis_ob.set(user, json.dumps(square_numbers))


# Get square numbers for a user and append the new move
def get_square_numbers(user, move):
	square_numbers = json.loads(redis_ob.get(user))  # Retrieve current square numbers
	square_numbers.append(move['square_number'])  # Add the new move
	square_numbers.sort()  # Sort the moves
	return square_numbers


# Namespace for handling game events
class GameStart(Namespace):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.current_user = []  # Current player's moves
		self.user1 = ''  # Player 1 username
		self.user2 = ''  # Player 2 username
		self.loser = ''  # Track the loser
		self.flag = True  # Flag to check if the game is ongoing
		self.swap_user = ['0']  # Track turns
		self.count = 0  # Count of moves
		# Winning combinations for Tic Tac Toe
		self.win_conditions = [
			[1, 2, 3], [1, 4, 7], [4, 5, 6], [2, 5, 8],
			[7, 8, 9], [3, 6, 9], [1, 5, 9], [3, 5, 7]
		]

	def on_connect(self):
		# Initialize game state when a user connects
		set_square_numbers('user1', [])  # Reset Player 1's moves
		set_square_numbers('user2', [])  # Reset Player 2's moves
		self.count = 0  # Reset move count
		self.flag = True  # Set game ongoing flag
		self.swap_user = ['0']  # Reset turn tracking
		print('user_connect')

	def on_move(self, move):
		# Handle a player's move
		if move['player'] != self.swap_user[-1]:  # Check if it's the correct player's turn

			# Assign usernames to player variables
			if self.user1 == '':
				self.user1 = move['username']
			if self.user1 != move['username'] and self.user2 == '':
				self.user2 = move['username']

			loser = '2' if move['player'] == '1' else '1'  # Determine loser based on player turn
			self.loser = self.user2 if self.user1 == move['username'] else self.user1

			# Update square numbers based on which player made the move
			if move['player'] == str(1):
				square_numbers = get_square_numbers('user1', move)
				print(square_numbers)
				set_square_numbers('user1', square_numbers)
				self.current_user = square_numbers
			else:
				square_numbers = get_square_numbers('user2', move)
				print(square_numbers)
				set_square_numbers('user2', square_numbers)
				self.current_user = square_numbers

			# Check for a win condition
			if len(self.current_user) > 2:
				for i in range(len(self.current_user) - 2):
					for j in range(i + 1, len(self.current_user) - 1):
						if [self.current_user[i], self.current_user[j], self.current_user[j + 1]] in self.win_conditions:
							# Emit events for win and loss
							emit('current_move', move, broadcast=True)
							emit('win', {'player': move['player'],
							             'square': [self.current_user[i], self.current_user[j],
							                        self.current_user[j + 1]],
							             'username': move['username']}, broadcast=True)

							emit('loss', {'player': loser, 'username': self.loser}, broadcast=True)
							self.flag = False  # Game has ended
							break

			# If no win, continue the game
			if self.flag is True:
				self.count += 1  # Increment move count
				if self.count == 9:  # Check for a draw
					print(self.count)
					emit('end_move', move, broadcast=True)  # Emit draw event
				else:
					print(self.count)
					emit('current_move', move, broadcast=True)  # Emit current move event
			else:
				emit('current_move', move, broadcast=True)  # Emit the move even after a win

			self.swap_user.append(move['player'])  # Switch turns
