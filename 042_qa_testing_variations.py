# testing_types.py
# Run with: python testing_types.py
# Illustrate different testing purposes using a small task service.
# Status numbers are returned values; this example does not run an HTTP server.

import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


def valid_title(title):
    # Check whether a title contains any non-whitespace characters.
    return bool(title.strip())


class TaskService:
    def __init__(self, capacity=100):
        # Store tasks in memory with a configurable maximum count.
        self.capacity = capacity
        self.tasks = []

        # Protect shared task data during concurrent additions and deletions.
        self.lock = Lock()

    def add(self, title):
        # Reject blank titles before attempting to modify shared state.
        if not valid_title(title):
            return 400, "Title required"

        with self.lock:
            # Keep the capacity check and insertion in one protected section.
            if len(self.tasks) >= self.capacity:
                return 503, "Capacity reached"

            self.tasks.append(title.strip())
            return 201, "Created"

    def delete(self, title):
        with self.lock:
            # Remove the first exact title match, or report that none exists.
            if title not in self.tasks:
                return 404, "Not found"

            self.tasks.remove(title)
            return 204, ""


class TestingTypes(unittest.TestCase):
    def test_component(self):
        # Test the title-validation function independently of the service.
        self.assertTrue(valid_title("Write README"))
        self.assertFalse(valid_title("   "))

    def test_integration(self):
        # Exercise a small data flow from service logic into SQLite.
        # The test performs the database insertion; the service itself
        # has no database persistence layer.
        connection = sqlite3.connect(":memory:")
        try:
            connection.execute(
                "CREATE TABLE tasks (title TEXT NOT NULL)"
            )

            service = TaskService()
            status, _ = service.add("Test integration")
            self.assertEqual(status, 201)

            # Store the service's output and retrieve it for comparison.
            connection.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (service.tasks[0],),
            )
            stored = connection.execute(
                "SELECT title FROM tasks"
            ).fetchone()[0]

            self.assertEqual(stored, "Test integration")
        finally:
            # Release the temporary database even if an assertion fails.
            connection.close()

    def test_sanity(self):
        # Make a focused check of basic task creation after a change.
        service = TaskService()
        status, _ = service.add("Write README")
        self.assertEqual(status, 201)
        self.assertIn("Write README", service.tasks)

    def test_regression(self):
        # Protect existing deletion behaviour against unintended changes.
        service = TaskService()
        service.add("Write README")
        status, _ = service.delete("Write README")
        self.assertEqual(status, 204)
        self.assertNotIn("Write README", service.tasks)

    def test_verification(self):
        # Compare implementation behaviour with an explicit requirement.
        requirement = "Blank task titles must be rejected"
        service = TaskService()
        status, _ = service.add("   ")

        self.assertEqual(status, 400, requirement)
        self.assertEqual(service.tasks, [], requirement)

    def test_validation(self):
        # Represent a user goal through a service-level scenario.
        # This does not exercise a complete interface or establish user acceptance.
        user_goal = "I can add a task and see it in my list"
        service = TaskService()

        service.add("Buy groceries")
        self.assertIn("Buy groceries", service.tasks, user_goal)

    def test_load(self):
        # Submit 20 additions through a pool of up to 10 worker threads.
        # Capacity exceeds demand, so every addition should succeed.
        # This checks concurrent correctness rather than response-time targets.
        service = TaskService(capacity=30)

        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(
                pool.map(
                    service.add,
                    [f"Task {number}" for number in range(20)],
                )
            )

        # Verify that all submitted tasks were accepted and retained.
        self.assertEqual(len(service.tasks), 20)
        self.assertTrue(all(status == 201 for status, _ in results))

    def test_stress(self):
        # Submit more additions than the service's configured storage capacity.
        # This models controlled capacity exhaustion rather than measuring
        # CPU, memory, or network saturation.
        service = TaskService(capacity=10)

        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(
                pool.map(
                    service.add,
                    [f"Task {number}" for number in range(25)],
                )
            )

        # Expect exactly 10 successful additions and 15 controlled rejections.
        statuses = [status for status, _ in results]
        self.assertEqual(statuses.count(201), 10)
        self.assertEqual(statuses.count(503), 15)
        self.assertEqual(len(service.tasks), 10)


if __name__ == "__main__":
    # Run the test methods and display each test's name and outcome.
    unittest.main(verbosity=2)