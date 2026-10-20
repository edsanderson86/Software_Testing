# test_pyramid.py
# Run with: python test_pyramid.py
# Illustrate a test pyramid with three unit tests, one integration test,
# and one broader test spanning HTTP handling and database storage.

import json
import sqlite3
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen


def normalize_title(title):
    # Apply the shared rule: trim surrounding whitespace and reject blank titles.
    title = title.strip()
    if not title:
        raise ValueError("Title required")
    return title


class TaskRepository:
    def __init__(self, connection):
        # Accept an existing connection so callers control database setup
        # and cleanup.
        self.connection = connection

    def add(self, title):
        # Normalize input before inserting it with a parameterized statement.
        cursor = self.connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (normalize_title(title),),
        )

        # Commit the insertion and return the generated task ID.
        self.connection.commit()
        return cursor.lastrowid

    def get(self, task_id):
        # Return the matching (id, title) tuple, or None when no task exists.
        return self.connection.execute(
            "SELECT id, title FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()


class TestPyramid(unittest.TestCase):
    # BASE: focused unit tests check individual rules without HTTP or storage.

    def test_unit_trims_spaces(self):
        # Confirm that surrounding spaces are removed.
        self.assertEqual(normalize_title("  Write README  "), "Write README")

    def test_unit_preserves_text(self):
        # Confirm that an already clean title remains unchanged.
        self.assertEqual(normalize_title("Test app"), "Test app")

    def test_unit_rejects_blank_title(self):
        # Confirm that whitespace-only input raises the expected exception.
        with self.assertRaises(ValueError):
            normalize_title("   ")

    # MIDDLE: an integration test checks repository logic together with SQLite.

    def test_integration_repository_and_database(self):
        # Use a temporary in-memory database isolated from other tests.
        connection = sqlite3.connect(":memory:")
        try:
            connection.execute(
                "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT)"
            )
            repository = TaskRepository(connection)

            # Verify that normalization, insertion, and retrieval work together.
            task_id = repository.add("  Write README  ")
            self.assertEqual(
                repository.get(task_id),
                (task_id, "Write README"),
            )
        finally:
            connection.close()

    # TOP: a broader test exercises a request through HTTP into storage.
    # It covers the API flow without a browser or a deployed environment.

    def test_end_to_end_http_request(self):
        # Create a named in-memory database for this demonstration.
        # Disabling the thread check permits the handler to use this connection;
        # it does not synchronize concurrent database operations.
        connection = sqlite3.connect(
            "file:pyramid_demo?mode=memory&cache=shared",
            uri=True,
            check_same_thread=False,
        )
        connection.execute(
            "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT)"
        )
        repository = TaskRepository(connection)

        # Define a local handler that uses the repository created above.
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                # Read and parse the submitted JSON body.
                # This simplified handler accepts POST requests at any path.
                length = int(self.headers.get("Content-Length", "0"))
                data = json.loads(self.rfile.read(length))

                try:
                    # Pass the title through the shared rule and database layer.
                    task_id = repository.add(data["title"])
                except ValueError:
                    # Translate title validation failure into an HTTP response.
                    self.send_response(400)
                    body = b'{"error":"Title required"}'
                else:
                    # Return the generated ID and the title read from storage.
                    self.send_response(201)
                    body = json.dumps(
                        {"id": task_id, "title": repository.get(task_id)[1]}
                    ).encode()

                # Describe and send the JSON response.
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                # Suppress request logs during test execution.
                pass

        # Start the local service on an available port.
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            # Send one task-creation request through the HTTP interface.
            request = Request(
                f"http://127.0.0.1:{server.server_port}/tasks",
                data=json.dumps({"title": "Write README"}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            # Verify the response status and decode the returned data.
            with urlopen(request, timeout=5) as response:
                self.assertEqual(response.status, 201)
                body = json.loads(response.read())

            # Check both the public response and the underlying stored record.
            self.assertEqual(body["title"], "Write README")
            self.assertEqual(
                repository.get(body["id"]),
                (body["id"], "Write README"),
            )
        finally:
            # Stop request handling before releasing the database connection.
            server.shutdown()
            server.server_close()
            thread.join()
            connection.close()


if __name__ == "__main__":
    # Discover and run all test methods with individual names and outcomes.
    unittest.main(verbosity=2)
    