from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import threading

hostName = "localhost"
serverPort = 8080


class Game:
    def __init__(self):
        self.max_players = None
        self.rules = 'chess'


games = {}


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
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
            game_id = 'wwwwwwww'
            self.wfile.write(game_id.encode('utf-8'))
            assert game_id not in games

            try:
                games[game_id] = Game()
            except json.JSONDecodeError:
                print('json decodererror')

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
