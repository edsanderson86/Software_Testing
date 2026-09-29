# end_to_end_bugzilla_example.py
# Run with: python end_to_end_bugzilla_example.py
#
# Tests a local task app from HTTP request to stored result.
# If the test fails, it files a defect in a LOCAL Bugzilla-style simulator.
# No external account or service is contacted.

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

tasks = {}
bugs = {}
next_task_id = 1
next_bug_id = 1


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global next_task_id, next_bug_id

        length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(length) or b"{}")

        if self.path == "/api/tasks":
            title = data.get("title", "").strip()
            if not title:
                self.respond(400, {"error": "Title required"})
                return

            task_id = next_task_id
            next_task_id += 1
            tasks[task_id] = {"id": task_id, "title": title, "done": False}
            self.respond(201, tasks[task_id])
            return

        if self.path == "/rest/bug":
            bug_id = next_bug_id
            next_bug_id += 1
            bugs[bug_id] = {"id": bug_id, **data}
            self.respond(201, {"id": bug_id})
            return

        self.respond(404, {"error": "Not found"})

    def do_GET(self):
        if self.path.startswith("/api/tasks/"):
            try:
                task_id = int(self.path.rsplit("/", 1)[1])
            except ValueError:
                self.respond(400, {"error": "Invalid task ID"})
                return

            task = tasks.get(task_id)
            self.respond(
                200 if task else 404,
                task or {"error": "Task not found"},
            )
            return

        self.respond(404, {"error": "Not found"})

    def respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
base_url = f"http://127.0.0.1:{server.server_port}"


def api_request(method, path, payload=None):
    request = Request(
        base_url + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"},
        method=method,
    )

    try:
        response = urlopen(request, timeout=5)
    except HTTPError as error:
        response = error

    with response:
        return response.status, json.loads(response.read())


def file_defect(title, expected, actual, steps):
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
    assert status == 201
    return body["id"]


def run_end_to_end_test():
    title = "Write README"

    # 1. Create a task through the app's HTTP API.
    create_status, created = api_request(
        "POST", "/api/tasks", {"title": title}
    )
    assert create_status == 201, f"Create returned {create_status}"

    # 2. Read it through a separate HTTP request.
    read_status, retrieved = api_request(
        "GET", f"/api/tasks/{created['id']}"
    )
    assert read_status == 200, f"Read returned {read_status}"
    assert retrieved["title"] == title
    assert retrieved["done"] is False

    print("PASS: task created and retrieved end to end")


try:
    try:
        run_end_to_end_test()
    except AssertionError as error:
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
        print(f"FAIL: local defect BUG-{bug_id} filed")
        print("Defect:", bugs[bug_id])
finally:
    server.shutdown()
    server.server_close()
    thread.join()