import wsgiref.simple_server
import urllib.parse
import http.cookies
import random
import Web_OOP

from string import ascii_uppercase, digits

# Necessary to globalize, since values should
# be the same for all clients
player1 = None
player2 = None
player1_sonar_choice = None
player2_sonar_choice = None
sonars = None
ui = Web_OOP.UI()
board = Web_OOP.Board()
board.generateRandomChests(3)
board.createBoard()

def app(env, sres):
	global player1
	global player2
	global player1_sonar_choice
	global player2_sonar_choice
	global sonars
	global ui
	global board

	headers = [('Content-Type', 'text/html; charset=utf-8')]
	path = env["PATH_INFO"]

	params = urllib.parse.parse_qs(env["QUERY_STRING"])
	
	# Wait for players to join
	if path == "/wait":
		sres('200 OK', headers)

		# Fill players
		if player1 == None:
			# Key represents the player, a unique key
			# will be generated here, ensuring that
			# only *this* person with a matching cookie
			# will be identified as the proper player
			key = "".join(random.choices(ascii_uppercase + digits, k=16))
			headers.append(("Set-Cookie", "key={}; expires=Thu, 01 Jan 6969 00:00:00 GMT".format(key)))
			player1 = key
			return ["Joined as Player 1!<br><a href='/choose'>Choose sonar count here!</a>".encode()]

		elif player2 == None:
			key = "".join(random.choices(ascii_uppercase + digits, k=16))
			headers.append(("Set-Cookie", "key={}; expires=Thu, 01 Jan 6969 00:00:00 GMT".format(key)))
			player2 = key
			return ["Joined as Player 2!<br><a href='/choose'>Choose sonar count here!</a>".encode()]
		else:
			return ["Game is full, sorry!".encode()]

	# Server endpoint representing whether or not
	# sonar count has been chosen
	elif path == "/count":
		sres('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])

		return [("True" if player1_sonar_choice != None and player2_sonar_choice != None else "False").encode()]

	else:
		# Choose how many sonars to play with
		if path == "/choose":
			sres('200 OK', headers)

			if sonars == None:
				# Get cookies
				if "HTTP_COOKIE" not in env:
					return ["Game is full, sorry!".encode()]
				cookies = http.cookies.SimpleCookie()
				cookies.load(env["HTTP_COOKIE"])

				# Get key
				if "key" not in cookies:
					return ["Game is full, sorry!".encode()]
				key = cookies["key"].value

				# Html page for choosing sonar count
				choose_html = """
				<!DOCTYPE html>
				<html>
					<body>
						<form action='/choose'>
							How many sonars would you like?<br>
							<input type='number' name='choice'>
						</form>
					</body>
				</html>
				""".encode()

				# User is player 1
				if key == player1:
					# User has chosen
					if "choice" in params:
						# Clamp choice to 0-40 range
						player1_sonar_choice = min(max(int(params["choice"][0]), 0), 40)
					else:
						return [choose_html]

				# User is player2
				elif key == player2:
					if "choice" in params:
						player2_sonar_choice = min(max(int(params["choice"][0]), 0), 40)
					else:
						return [choose_html]
				
				# User is invalid
				else:
					return ["Invalid user, sorry!".encode()]
				
				# Waiting for other player to choose
				if player1_sonar_choice == None or player2_sonar_choice == None:
					return ["""
					<!DOCTYPE html>
					<html>
						<body>
							Waiting for other player to choose sonar count...
							<script>
								// Check if players have chosen sonar 
								// counts every second
								let int;
								int = setInterval(() => {

									// Send 'GET' request to '/count'
									const xhr = new XMLHttpRequest();
									xhr.open('GET', '/count');
									xhr.onload = () => {
										const {response} = xhr;

										// If both players have chosen
										if (response == 'True') {
											clearInterval(int);
											window.location.reload();
										}
									};
									xhr.send();
								}, 1000);
							</script>
						</body>
					</html>
					""".encode()]
				
				# Both players have chosen, redirect to game
				return ["Both players have chosen!<br><a href='/game'>Redirect to game here!</a>".encode()]
			else:
				return ["Sonar count has already been chosen, sorry!".encode()]

		# Play game
		elif path == "/game":
			sres('200 OK', headers)
			# Choose either player's choice
			if sonars == None:
				sonars = random.choice([player1_sonar_choice, player2_sonar_choice])
			if not params:
				return [ui.initialize().encode()]
			elif "instr" in params and params["instr"][0].lower() == "yes":
				return [ui.showInstructions().encode()]
			elif "x" and "y" in params:
				x = params["x"][0]
				y = params["y"][0]
				message = ui.enterPlayerMove(x,y,board)
				return [ui.printer(board,message).encode()]
			else:
				return [ui.printer(board,'').encode()]
		elif path == "/":
			sres('200 OK', headers)

			return ["S O N A R !<br><a href='/wait'>Click here to join the game!</a>".encode()]	
		elif path == "/index.css":
			sres('200 OK', headers)
			return [open("index.css").read().encode()]
		else:
			sres('404 NOT FOUND', headers)

			return ["404 Not found!".encode()]

httpd = wsgiref.simple_server.make_server('', 8000, app)
httpd.serve_forever()