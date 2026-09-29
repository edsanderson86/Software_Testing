# test_pyramid.py
# Run with: python test_pyramid.py

import json
import sqlite3
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen


def normalize_title(title):
    """Application rule used by every layer."""
    title = title.strip()
    if not title:
        raise ValueError("Title required")
    return title


class TaskRepository:
    def __init__(self, connection):
        self.connection = connection

    def add(self, title):
        cursor = self.connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (normalize_title(title),),
        )
        self.connection.commit()
        return cursor.lastrowid

    def get(self, task_id):
        return self.connection.execute(
            "SELECT id, title FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()


class TestPyramid(unittest.TestCase):
    # BASE: many fast unit tests for individual rules.
    def test_unit_trims_spaces(self):
        self.assertEqual(normalize_title("  Write README  "), "Write README")

    def test_unit_preserves_text(self):
        self.assertEqual(normalize_title("Test app"), "Test app")

    def test_unit_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            normalize_title("   ")

    # MIDDLE: fewer integration tests for components working together.
    def test_integration_repository_and_database(self):
        connection = sqlite3.connect(":memory:")
        try:
            connection.execute(
                "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT)"
            )
            repository = TaskRepository(connection)

            task_id = repository.add("  Write README  ")
            self.assertEqual(
                repository.get(task_id),
                (task_id, "Write README"),
            )
        finally:
            connection.close()

    # TOP: a small number of end-to-end tests across HTTP and storage.
    def test_end_to_end_http_request(self):
        connection = sqlite3.connect(
            "file:pyramid_demo?mode=memory&cache=shared",
            uri=True,
            check_same_thread=False,
        )
        connection.execute(
            "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT)"
        )
        repository = TaskRepository(connection)

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                data = json.loads(self.rfile.read(length))

                try:
                    task_id = repository.add(data["title"])
                except ValueError:
                    self.send_response(400)
                    body = b'{"error":"Title required"}'
                else:
                    self.send_response(201)
                    body = json.dumps(
                        {"id": task_id, "title": repository.get(task_id)[1]}
                    ).encode()

                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            request = Request(
                f"http://127.0.0.1:{server.server_port}/tasks",
                data=json.dumps({"title": "Write README"}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urlopen(request, timeout=5) as response:
                self.assertEqual(response.status, 201)
                body = json.loads(response.read())

            self.assertEqual(body["title"], "Write README")
            self.assertEqual(
                repository.get(body["id"]),
                (body["id"], "Write README"),
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
            connection.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
    
    