# http_methods_status_codes.py
# Run with: python http_methods_status_codes.py

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

tasks = {1: "Write README"}
next_id = 2


class TaskHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/tasks/1" and 1 in tasks:
            self.reply(200, tasks[1].encode())  # OK
        else:
            self.reply(404, b"Task not found")  # Not Found

    def do_POST(self):
        global next_id

        if self.path != "/tasks":
            self.reply(404, b"Not found")
            return

        title = self.read_body().strip()
        if not title:
            self.reply(400, b"Title required")  # Bad Request
            return

        task_id = next_id
        next_id += 1
        tasks[task_id] = title.decode()
        self.reply(201, f"Created task {task_id}".encode())  # Created

    def do_PUT(self):
        if self.path != "/tasks/1" or 1 not in tasks:
            self.reply(404, b"Task not found")
            return

        title = self.read_body().strip()
        if not title:
            self.reply(400, b"Title required")
            return

        tasks[1] = title.decode()
        self.reply(200, b"Task updated")  # OK

    def do_DELETE(self):
        if self.path != "/tasks/1" or 1 not in tasks:
            self.reply(404, b"Task not found")
            return

        del tasks[1]
        self.reply(204, b"")  # No Content

    def read_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length)

    def reply(self, status, body):
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), TaskHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f"http://127.0.0.1:{server.server_port}"


def send(method, path, body=None):
    request = Request(
        base + path,
        data=body.encode() if body is not None else None,
        method=method,
    )
    try:
        response = urlopen(request)
    except HTTPError as error:
        response = error

    with response:
        print(method, path, "->", response.status, response.read().decode())


try:
    send("GET", "/tasks/1")                  # 200
    send("POST", "/tasks", "Test the app")     # 201
    send("POST", "/tasks", "   ")              # 400
    send("PUT", "/tasks/1", "Update README")   # 200
    send("DELETE", "/tasks/1")                 # 204
    send("GET", "/tasks/1")                    # 404
finally:
    server.shutdown()
    server.server_close()
    thread.join()