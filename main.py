from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import threading
import random
import secrets
import time

hostName = "localhost"
serverPort = 8080

# TODO: give joining players a token because now they can spam reload and the server thinks many players are joining


def new_game_id():
    def game_id():
        return ''.join([random.choice('aeouiqwkhq') for _ in range(8)])
    global games

    game = game_id()
    if game in games:
        game = game[:-3].rjust(8, 'Q')
        if game in games:
            return None
        else:
            return game
    else:
        return game


class Game:
    def __init__(self, game_id):
        self.max_players = None
        self.rules = {'board': ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br',
                                'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp',
                                ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
                                ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
                                ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
                                ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
                                'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp',
                                'wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']}
        self.game_id = game_id
        self.tokens = [secrets.token_hex(32)]
        self.players = 1
        self.board = None
        self.times = []


games = {}

# TODO: a thread that monitors timeouts and removes games


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        global games
        cookie = self.headers['Cookie']

        theme = None

        split = cookie.split(';')
        for c in split:
            c = c.removeprefix(' ')
            pair = c.split('=')
            if len(pair) != 2:
                continue
            if pair[0] != 'theme':
                continue
            if pair[1] not in ['light', 'dark']:
                continue
            theme = pair[1]
        if theme is None:
            theme = 'light'

        # if self.rfile.tell() != 0:
        #     self.rfile.seek(0)
        #     print(self.rfile.read())

        self.send_response(200)

        path = urllib.parse.urlparse(self.path)
        base_path = path.path
        path_query = urllib.parse.parse_qs(path.query)
        print(base_path, path_query)

        if base_path.startswith('/api'):
            self.send_header("Content-type", "application/json")
        elif base_path.endswith('.html'):
            self.send_header("Content-type", "text/html")
        elif base_path.endswith('.js'):
            self.send_header("Content-type", "application/javascript")
        elif base_path.endswith('.css'):
            self.send_header("Content-type", "text/css")
        elif base_path.endswith('.ttf'):
            self.send_header("Content-type", "font/ttf")
        elif base_path.endswith('.ico'):
            self.send_header("Content-type", "image/x-icon")
        elif base_path != '/':
            print('a')

        if base_path == '/':
            base_path = '/index.html'
        if base_path[0] != '/':
            print(f"incorrect path '{base_path}'")
            self.send_response(404)
            return

        if base_path == '/api/game-id':
            game_id = new_game_id()
            self.wfile.write(game_id.encode('utf-8'))
            assert game_id not in games

            games[game_id] = Game(game_id)

            self.wfile.write(('\n' + games[game_id].tokens[0]).encode('utf-8'))

            return
        elif base_path == '/api/rules':
            if 'game-id' in path_query:
                game_id = path_query['game-id'][0]
            else:
                self.wfile.write('id'.encode('utf-8'))
                return

            if 'token' in path_query:
                token = path_query['token'][0]
            else:
                self.wfile.write('token'.encode('utf-8'))
                return

            if game_id not in games:
                self.wfile.write('unknown id'.encode('utf-8'))
                return
            game = games[game_id]
            if game.tokens[0] != token:
                self.wfile.write('token'.encode('utf-8'))
                return

            if 'max-players' in path_query:
                max_players = path_query['max-players'][0]
                try:
                    game.max_players = int(max_players)
                except ValueError:
                    self.wfile.write('rules'.encode('utf-8'))
                    return
            else:
                self.wfile.write('rules'.encode('utf-8'))
                return

            self.wfile.write('ok'.encode('utf-8'))
            return

        elif base_path == '/api/players':
            if 'game-id' in path_query:
                game_id = path_query['game-id'][0]
            else:
                self.wfile.write('id'.encode('utf-8'))
                return

            if game_id not in games:
                self.wfile.write('id'.encode('utf-8'))
                return

            game = games[game_id]
            if game.max_players is not None and game.max_players == game.players:
                self.wfile.write(b'start')
            else:
                self.wfile.write(str(game.players).encode('utf-8'))

            if 'token' in path_query:
                token = path_query['token'][0]
                i = game.tokens.index(token)
                if i == -1:
                    return

                assert len(game.tokens) == game.players
                if len(game.times) < game.players:
                    for j in range(game.players - len(game.times)):
                        game.times.append(time.time())

                game.times[i] = time.time()

            return

        elif base_path == '/api/join':
            if 'game-id' in path_query:
                game_id = path_query['game-id'][0]
            else:
                self.wfile.write('id'.encode('utf-8'))
                return

            if game_id not in games:
                self.wfile.write('u-id'.encode('utf-8'))
                return

            game = games[game_id]
            if game.max_players is None:
                self.wfile.write('uninit'.encode('utf-8'))
                return

            if game.players + 1 > game.max_players:
                self.wfile.write('full'.encode('utf-8'))  # TODO: spectate
                return

            game.players += 1
            game.tokens.append(secrets.token_hex(32))
            self.wfile.write(game.tokens[-1].encode('utf-8'))
            return

        elif base_path == '/api/get-rules':
            if 'game-id' in path_query:
                game_id = path_query['game-id'][0]
            else:
                self.wfile.write('id'.encode('utf-8'))
                return

            if game_id not in games:
                self.wfile.write('u-id'.encode('utf-8'))
                return

            game = games[game_id]
            if game.max_players is None:
                self.wfile.write('uninit'.encode('utf-8'))
                return

            out = {
                'max_players': game.max_players,
                'rules': game.rules
            }

            self.wfile.write(json.dumps(out).encode('utf-8'))
            return

        if base_path == '/style.css' and theme == 'dark':
            base_path = '/style-dark.css'

        self.path = './pages' + base_path  # TODO: you could do ../ and access every file on the system

        if self.path.endswith('.png') or self.path.endswith('.ttf'):
            self.send_header('cache-control', 'private, max-age=31536000')

        self.end_headers()

        try:
            with open(self.path, 'rb') as file:
                self.wfile.write(file.read())
                return
        except FileNotFoundError:
            print(f"file '{self.path}' not found")

            self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
            self.wfile.write(bytes("<p>Request: <code>%s</code></p>" % base_path, "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<p>404</p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), Server)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
