# http_methods_status_codes.py
# Run with: python http_methods_status_codes.py
# Demonstrate retrieving, creating, updating, and deleting tasks over HTTP.

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Store tasks in memory, using a numeric ID to identify each task.
# Data is reset whenever the script restarts.
tasks = {1: "Write README"}
next_id = 2


class TaskHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # This example supports retrieving task 1 only.
        if self.path == "/tasks/1" and 1 in tasks:
            self.reply(200, tasks[1].encode())  # OK
        else:
            self.reply(404, b"Task not found")  # Not Found

    def do_POST(self):
        # Update the shared counter when assigning a new task ID.
        global next_id

        # Accept task creation only at the collection URL.
        if self.path != "/tasks":
            self.reply(404, b"Not found")
            return

        # Reject an empty or whitespace-only request body.
        title = self.read_body().strip()
        if not title:
            self.reply(400, b"Title required")  # Bad Request
            return

        # Store the title under a new ID and confirm creation.
        task_id = next_id
        next_id += 1
        tasks[task_id] = title.decode()
        self.reply(201, f"Created task {task_id}".encode())  # Created

    def do_PUT(self):
        # Require an existing task at the supported URL.
        if self.path != "/tasks/1" or 1 not in tasks:
            self.reply(404, b"Task not found")
            return

        # Validate the replacement title before changing the task.
        title = self.read_body().strip()
        if not title:
            self.reply(400, b"Title required")
            return

        # Replace the existing title and confirm the update.
        tasks[1] = title.decode()
        self.reply(200, b"Task updated")  # OK

    def do_DELETE(self):
        # Check that the requested task exists before deleting it.
        if self.path != "/tasks/1" or 1 not in tasks:
            self.reply(404, b"Task not found")
            return

        # Confirm successful deletion without a response body.
        del tasks[1]
        self.reply(204, b"")  # No Content

    def read_body(self):
        # Read the number of body bytes specified by the client.
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length)

    def reply(self, status, body):
        # Send the status code, body length, and response bytes.
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Suppress standard request logs to keep results easy to read.
        pass


# Start a server accessible only from this computer.
# Port 0 lets the operating system select an available port.
server = ThreadingHTTPServer(("127.0.0.1", 0), TaskHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f"http://127.0.0.1:{server.server_port}"


def send(method, path, body=None):
    # Build a request with the chosen method and optional text body.
    request = Request(
        base + path,
        data=body.encode() if body is not None else None,
        method=method,
    )

    try:
        response = urlopen(request)
    except HTTPError as error:
        # Treat HTTP error responses as readable responses so their
        # status codes and messages can also be displayed.
        response = error

    with response:
        print(method, path, "->", response.status, response.read().decode())


try:
    # Retrieve the original task.
    send("GET", "/tasks/1")                   # 200 OK

    # Create a second task with a valid title.
    send("POST", "/tasks", "Test the app")    # 201 Created

    # Demonstrate rejection of a blank title.
    send("POST", "/tasks", "   ")            # 400 Bad Request

    # Replace the first task's title.
    send("PUT", "/tasks/1", "Update README")  # 200 OK

    # Delete the first task.
    send("DELETE", "/tasks/1")               # 204 No Content

    # Confirm that the deleted task can no longer be retrieved.
    send("GET", "/tasks/1")                  # 404 Not Found
finally:
    # Release server resources even if a request fails.
    server.shutdown()
    server.server_close()
    thread.join()