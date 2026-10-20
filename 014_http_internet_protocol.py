# http_protocol_example.py
# Run with: python http_protocol_example.py
# Demonstrates a local HTTP request over TCP and a JSON response.

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen


# Define how the server handles incoming requests.
class TaskHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve the task list only at the /tasks path.
        if self.path != "/tasks":
            self.send_error(404, "Not found")
            return

        # Convert task data into JSON, then encode it as UTF-8 bytes.
        body = json.dumps({"tasks": ["Write README", "Test the app"]}).encode()

        # Send a successful status and describe the response body.
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))

        # Finish the headers before sending the body bytes.
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Suppress standard request logs to keep demonstration output clear.
        pass


# Listen on this computer only.
# Port 0 asks the operating system to choose an available port.
server = ThreadingHTTPServer(("127.0.0.1", 0), TaskHandler)

# Run the server in a background thread so the client can run below.
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()

try:
    # Build the URL using the port assigned to the server.
    url = f"http://127.0.0.1:{server.server_port}/tasks"

    # Open a TCP connection and send an HTTP GET request.
    # The context manager closes the response after use.
    with urlopen(url, timeout=5) as response:
        # Display a request summary, followed by the received response details.
        print("Request: GET /tasks HTTP")
        print("Status:", response.status)
        print("Content-Type:", response.headers["Content-Type"])

        # Read the response bytes and decode them into text for display.
        print("Body:", response.read().decode())
finally:
    # Stop the server and release its socket even if the request fails.
    server.shutdown()
    server.server_close()

    # Wait for the background server thread to finish.
    thread.join()

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