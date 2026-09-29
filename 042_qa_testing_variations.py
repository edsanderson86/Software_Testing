# testing_types.py
# Run with: python testing_types.py

import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


def valid_title(title):
    """Component under test."""
    return bool(title.strip())


class TaskService:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.tasks = []
        self.lock = Lock()

    def add(self, title):
        if not valid_title(title):
            return 400, "Title required"

        with self.lock:
            if len(self.tasks) >= self.capacity:
                return 503, "Capacity reached"

            self.tasks.append(title.strip())
            return 201, "Created"

    def delete(self, title):
        with self.lock:
            if title not in self.tasks:
                return 404, "Not found"

            self.tasks.remove(title)
            return 204, ""


class TestingTypes(unittest.TestCase):
    def test_component(self):
        # Test one function in isolation.
        self.assertTrue(valid_title("Write README"))
        self.assertFalse(valid_title("   "))

    def test_integration(self):
        # Check that application logic works with SQLite storage.
        connection = sqlite3.connect(":memory:")
        try:
            connection.execute(
                "CREATE TABLE tasks (title TEXT NOT NULL)"
            )

            service = TaskService()
            status, _ = service.add("Test integration")
            self.assertEqual(status, 201)

            connection.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (service.tasks[0],),
            )
            stored = connection.execute(
                "SELECT title FROM tasks"
            ).fetchone()[0]

            self.assertEqual(stored, "Test integration")
        finally:
            connection.close()

    def test_sanity(self):
        # Quick check that the main feature works after a change.
        service = TaskService()
        status, _ = service.add("Write README")
        self.assertEqual(status, 201)
        self.assertIn("Write README", service.tasks)

    def test_regression(self):
        # Check an existing behavior that a new change might break.
        service = TaskService()
        service.add("Write README")
        status, _ = service.delete("Write README")
        self.assertEqual(status, 204)
        self.assertNotIn("Write README", service.tasks)

    def test_verification(self):
        # Verify implementation against a written requirement.
        requirement = "Blank task titles must be rejected"
        service = TaskService()
        status, _ = service.add("   ")

        self.assertEqual(status, 400, requirement)
        self.assertEqual(service.tasks, [], requirement)

    def test_validation(self):
        # Validate a user goal through an end-to-end scenario.
        user_goal = "I can add a task and see it in my list"
        service = TaskService()

        service.add("Buy groceries")
        self.assertIn("Buy groceries", service.tasks, user_goal)

    def test_load(self):
        # Expected load: 20 concurrent requests, capacity 30.
        service = TaskService(capacity=30)

        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(
                pool.map(
                    service.add,
                    [f"Task {number}" for number in range(20)],
                )
            )

        self.assertEqual(len(service.tasks), 20)
        self.assertTrue(all(status == 201 for status, _ in results))

    def test_stress(self):
        # Beyond capacity: failures should be controlled.
        service = TaskService(capacity=10)

        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(
                pool.map(
                    service.add,
                    [f"Task {number}" for number in range(25)],
                )
            )

        statuses = [status for status, _ in results]
        self.assertEqual(statuses.count(201), 10)
        self.assertEqual(statuses.count(503), 15)
        self.assertEqual(len(service.tasks), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)