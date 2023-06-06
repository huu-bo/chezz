from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import threading
import random
import secrets

hostName = "localhost"
serverPort = 8080


def new_game_id():
    def game_id():
        return ''.join([random.choice('aeouiqwkghq') for i in range(8)])
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
        self.rules = 'chess'
        self.game_id = game_id
        self.tokens = [secrets.token_hex(32)]


games = {}


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        global games

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
            if games[game_id].tokens[0] != token:
                self.wfile.write('token'.encode('utf-8'))
                return

            self.wfile.write('ok'.encode('utf-8'))
            return

        self.path = './pages' + base_path

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