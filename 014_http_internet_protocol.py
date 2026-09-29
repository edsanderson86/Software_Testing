# http_protocol_example.py
# Run with: python http_protocol_example.py
# Demonstrates: TCP connection -> HTTP request -> HTTP response -> JSON body

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen


class TaskHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/tasks":
            self.send_error(404, "Not found")
            return

        body = json.dumps({"tasks": ["Write README", "Test the app"]}).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), TaskHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()

try:
    url = f"http://127.0.0.1:{server.server_port}/tasks"

    with urlopen(url, timeout=5) as response:
        print("Request: GET /tasks HTTP")
        print("Status:", response.status)
        print("Content-Type:", response.headers["Content-Type"])
        print("Body:", response.read().decode())
finally:
    server.shutdown()
    server.server_close()
    thread.join()