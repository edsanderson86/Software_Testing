# end_to_end_bugzilla_example.py
# Run with: python end_to_end_bugzilla_example.py
#
# Test task creation and retrieval through a local HTTP API.
# If an assertion fails, submit a defect to a local Bugzilla-style simulator.
# No external account or service is contacted.
# Tasks and defects are stored in memory and do not survive a restart.

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Keep task records and simulated defect reports in separate dictionaries.
tasks = {}
bugs = {}
next_task_id = 1
next_bug_id = 1


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Update the shared counters when creating tasks or defects.
        # This sequential demonstration does not synchronize concurrent writes.
        global next_task_id, next_bug_id

        # Read the request body and decode its JSON content.
        length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(length) or b"{}")

        if self.path == "/api/tasks":
            # Validate the title before assigning an ID or storing a task.
            title = data.get("title", "").strip()
            if not title:
                self.respond(400, {"error": "Title required"})
                return

            # Store a new task with an initial completion state of False.
            task_id = next_task_id
            next_task_id += 1
            tasks[task_id] = {"id": task_id, "title": title, "done": False}
            self.respond(201, tasks[task_id])
            return

        if self.path == "/rest/bug":
            # Accept and store a simplified defect submission locally.
            # This simulator does not implement full Bugzilla validation.
            bug_id = next_bug_id
            next_bug_id += 1
            bugs[bug_id] = {"id": bug_id, **data}
            self.respond(201, {"id": bug_id})
            return

        # Reject paths without a supported POST operation.
        self.respond(404, {"error": "Not found"})

    def do_GET(self):
        if self.path.startswith("/api/tasks/"):
            # Extract the numeric task ID from the final URL segment.
            try:
                task_id = int(self.path.rsplit("/", 1)[1])
            except ValueError:
                self.respond(400, {"error": "Invalid task ID"})
                return

            # Return the stored task or a not-found response.
            task = tasks.get(task_id)
            self.respond(
                200 if task else 404,
                task or {"error": "Task not found"},
            )
            return

        self.respond(404, {"error": "Not found"})

    def respond(self, status, data):
        # Serialize the response and supply its content type and byte length.
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Suppress request logs so test and defect output remain clear.
        pass


# Start a local server on an available port in a background thread.
server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
base_url = f"http://127.0.0.1:{server.server_port}"


def api_request(method, path, payload=None):
    # Build a request with an optional JSON body.
    request = Request(
        base_url + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"},
        method=method,
    )

    try:
        response = urlopen(request, timeout=5)
    except HTTPError as error:
        # Return HTTP error statuses and bodies for the caller to inspect.
        # Connection failures and timeouts still propagate as exceptions.
        response = error

    with response:
        return response.status, json.loads(response.read())


def file_defect(title, expected, actual, steps):
    # Format reproduction steps and outcomes into a readable description.
    # Submit the report to the simulator running on the same local server.
    status, body = api_request(
        "POST",
        "/rest/bug",
        {
            "product": "Task Tracker",
            "component": "Tasks",
            "summary": title,
            "version": "1.0",
            "description": (
                "Steps to reproduce:\n"
                + "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))
                + f"\n\nExpected: {expected}\nActual: {actual}"
            ),
        },
    )

    # Verify that the simulator accepted the report and return its reference.
    assert status == 201
    return body["id"]


def run_end_to_end_test():
    title = "Write README"

    # Create a task through HTTP rather than accessing server data directly.
    create_status, created = api_request(
        "POST", "/api/tasks", {"title": title}
    )
    assert create_status == 201, f"Create returned {create_status}"

    # Correlate the next request using the ID returned during creation.
    read_status, retrieved = api_request(
        "GET", f"/api/tasks/{created['id']}"
    )

    # Verify retrieval, the saved title, and the initial completion state.
    # This covers the API-to-memory flow without a browser or database.
    assert read_status == 200, f"Read returned {read_status}"
    assert retrieved["title"] == title
    assert retrieved["done"] is False

    print("PASS: task created and retrieved end to end")


try:
    try:
        # Run the creation-and-retrieval scenario.
        run_end_to_end_test()
    except AssertionError as error:
        # File a local defect when an assertion fails.
        # Other exception types are not converted into reports here.
        bug_id = file_defect(
            title="Task creation end-to-end test failed",
            expected="Created task can be retrieved with the same title",
            actual=str(error),
            steps=[
                "POST a task with title 'Write README'",
                "GET the task using the returned ID",
                "Compare the returned title and completion status",
            ],
        )

        # Display the submitted report for review.
        # This handled failure does not set a nonzero process exit code.
        print(f"FAIL: local defect BUG-{bug_id} filed")
        print("Defect:", bugs[bug_id])
finally:
    # Stop the server and release its socket even when the scenario fails.
    server.shutdown()
    server.server_close()
    thread.join()